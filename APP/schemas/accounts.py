from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal

from APP.schemas.transactions import Transaction


class Account(BaseModel):
    id: int = Field(..., description='Уникальный идентификатор')
    amount: Decimal = Field(..., gt=0, description="Сумма")
    transactions: list[Transaction] = Field(..., description='Транзакции счета')

    model_config = ConfigDict(from_attributes=True)