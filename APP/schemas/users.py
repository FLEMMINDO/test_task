from pydantic import BaseModel, Field, ConfigDict, EmailStr

from APP.schemas.accounts import Account


class User(BaseModel):
    """
    Модель для пользователя
    используется в GET запросах
    """
    id: int = Field(..., description='Уникальный идентификатор')
    full_name: str = Field(..., description='Полное наименование')
    email: EmailStr = Field(..., description='Электронная почта')

    model_config = ConfigDict(from_attributes=True)


class UserCreateUpdate(BaseModel):
    full_name: str = Field(..., description='Полное наименование')
    email: str = Field(..., description='Электронная почта')
    password: str = Field(..., description='Пароль')


class FullUser(BaseModel):
    id: int = Field(..., description='Уникальный идентификатор')
    full_name: str = Field(..., description='Полное наименование')
    email: str = Field(..., description='Электронная почта')
    accounts: list[Account] = Field(..., description='Счета')
