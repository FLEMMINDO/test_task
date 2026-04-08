from pydantic import BaseModel, Field


class RefreshTokenRequest(BaseModel):
    """
    Модель для обновления токена
    используется в POST запросах
    """
    refresh_token: str = Field(..., detail='Refresh token')
