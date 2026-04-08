from pydantic import BaseModel, Field, ConfigDict, EmailStr

from APP.schemas.accounts import Account


class User(BaseModel):
    """
    Модель для информации пользователя
    используется в GET запросах
    """
    id: int = Field(..., description='Уникальный идентификатор')
    full_name: str = Field(..., description='Полное наименование')
    email: EmailStr = Field(..., description='Электронная почта')

    model_config = ConfigDict(from_attributes=True)


class UserCreateUpdate(BaseModel):
    """
    Модель для создания пользователя
    используется в POST/PUT запросах
    """
    full_name: str = Field(..., description='Полное наименование')
    email: str = Field(..., description='Электронная почта')
    password: str = Field(..., description='Пароль')


class FullUser(BaseModel):
    """
    Модель для полной информации пользователя
    используется в GET запросах
    """
    id: int = Field(..., description='Уникальный идентификатор')
    full_name: str = Field(..., description='Полное наименование')
    email: str = Field(..., description='Электронная почта')
    accounts: list[Account] = Field(..., description='Счета')
