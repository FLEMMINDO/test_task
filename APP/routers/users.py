import jwt
import os
from dotenv import load_dotenv
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from APP.models.users import User as UserModel
from APP.models.accounts import Account as AccountModel
from APP.schemas.users import User as UserSchema, UserCreateUpdate, FullUser as FullUserSchema
from APP.schemas.tokens import RefreshTokenRequest
from APP.db_depends import get_async_db
from APP.auth import (hash_password, verify_password, create_access_token, create_refresh_token,
                      get_current_user, get_current_admin)


router = APIRouter(prefix="/users", tags=["users"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("HASH_ALGORITHM")


@router.get('/list', response_model=list[FullUserSchema], status_code=status.HTTP_200_OK)
async def get_users(
        user: UserModel = Depends(get_current_admin),
        db: AsyncSession = Depends(get_async_db)
):
    """
    Получение списка пользователей и счетов с балансами (admin_endpoint)
    """

    db_users = await db.scalars(
        select(UserModel)
        .options(
            selectinload(UserModel.accounts).selectinload(AccountModel.transactions),
        )
    )

    return db_users


@router.get('/info', response_model=UserSchema, status_code=status.HTTP_200_OK)
async def get_user(
        user: UserModel = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    db_user = (await db.scalars(select(UserModel).where(UserModel.id == user.id))).first()

    return db_user


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
        new_user: UserCreateUpdate,
        user: UserModel = Depends(get_current_admin),
        db: AsyncSession = Depends(get_async_db)
):
    """
    Регистрирует нового пользователя с ролью "user"
    """

    result = await db.scalars(select(UserModel).where(UserModel.email == new_user.email))
    if result.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email already registered")

    result = await db.scalars(select(UserModel).where(UserModel.full_name == new_user.full_name))
    if result.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Username already registered')

    db_user = UserModel(
        email=new_user.email,
        full_name=new_user.full_name,
        hashed_password=hash_password(new_user.password)
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


@router.put("/{user_id}", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def update_user(user_id: int,
                      user: UserCreateUpdate,
                      current_user: UserModel = Depends(get_current_admin),
                      db: AsyncSession = Depends(get_async_db)):
    """
    Обновляет данные пользователя по ID
    """

    result = await db.scalars(select(UserModel).where(UserModel.id == user_id))
    db_user = result.first()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {current_user.id} not found")

    uniq_name_q = select(UserModel).where(UserModel.full_name == user.full_name)

    uniq_usr = (await db.scalars(uniq_name_q)).first()
    if uniq_usr:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User with this full_name already exist')

    uniq_email_q = select(UserModel).where(UserModel.email == user.email)

    uniq_usr = (await db.scalars(uniq_email_q)).first()
    if uniq_usr:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User with this email already exist')

    await db.execute(update(UserModel)
                     .where(UserModel.id == user_id)
                     .values(full_name=user.full_name, email=user.email, hashed_password=hash_password(user.password)))

    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.delete("/{user_id}", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def delete_user(user_id: int,
                      current_user: UserModel = Depends(get_current_admin),
                      db: AsyncSession = Depends(get_async_db)):
    """
    Удаляет пользователя по ID
    """

    result = await db.scalars(select(UserModel).where(UserModel.id == user_id))
    db_user = result.first()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {current_user.id} not found")

    await db.delete(db_user)
    await db.commit()

    return {'status': 'success', 'detail': 'user deleted'}


@router.post("/token")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_async_db)
):
    """
    Аутентифицирует пользователя и возвращает JWT с email, role и id.
    """
    result = await db.scalars(
        select(UserModel).where(UserModel.email == form_data.username))

    user = result.first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
    refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role, "id": user.id})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh-token")
async def refresh_token(
    body: RefreshTokenRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Обновляет refresh-токен, принимая старый refresh-токен в теле запроса.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    old_refresh_token = body.refresh_token

    try:
        payload = jwt.decode(old_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")

        # Проверяем, что токен действительно refresh
        if email is None or token_type != "refresh":
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        # refresh-токен истёк
        raise credentials_exception
    except jwt.PyJWTError:
        # подпись неверна или токен повреждён
        raise credentials_exception

    # Проверяем, что пользователь существует и активен
    result = await db.scalars(
        select(UserModel).where(
            UserModel.email == email
        )
    )
    user = result.first()
    if user is None:
        raise credentials_exception

    # Генерируем новый refresh-токен
    new_refresh_token = create_refresh_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )

    return {
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/access-token")
async def access_token(
    body: RefreshTokenRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Обновляет access-токен, принимая старый refresh-токен в теле запроса.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    refresh_token = body.refresh_token

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")

        # Проверяем, что токен действительно refresh
        if email is None or token_type != "refresh":
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        # refresh-токен истёк
        raise credentials_exception
    except jwt.PyJWTError:
        # подпись неверна или токен повреждён
        raise credentials_exception

    # Проверяем, что пользователь существует и активен
    result = await db.scalars(
        select(UserModel).where(
            UserModel.email == email
        )
    )
    user = result.first()
    if user is None:
        raise credentials_exception

    # Генерируем новый access-токен
    new_access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }