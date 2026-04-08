from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime


class Transaction(BaseModel):
    """
    Модель для валидации транзакции
    вложенная модель в Accounts
    """
    id: int = Field(..., description='Уникальный идентификатор')
    transaction_id: str = Field(..., description='Уникальный идентификатор транзакции')
    amount: Decimal = Field(..., description='Сумма транзакции')
    timestamp: datetime = Field(..., description="TIMESTAMP транзакции")

    model_config = ConfigDict(from_attributes=True)