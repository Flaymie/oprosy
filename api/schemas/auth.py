"""
Pydantic схемы для аутентификации
"""
from pydantic import BaseModel


class InitDataValidation(BaseModel):
    """Схема для валидации initData"""
    init_data: str


class AuthResponse(BaseModel):
    """Схема ответа после валидации"""
    user_id: int
    telegram_id: int
    is_admin: bool
    username: str | None = None
    first_name: str | None = None
