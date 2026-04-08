from pydantic import BaseModel, Field, ConfigDict, Extra
from decimal import Decimal


class Payment(BaseModel):
    """
    Модель для валидации платежа
    используется в вебхуке
    """
    transaction_id: str = Field(..., description='Уникальный идентификатор транзакции')
    user_id: int = Field(..., description="Уникальный идентификатор пользователя")
    account_id: int = Field(..., description='Уникальный идентификатор счёта')
    amount: Decimal = Field(..., gt=0, description='Сумма транзакции')

    model_config = ConfigDict(from_attributes=True, extra='forbid')
