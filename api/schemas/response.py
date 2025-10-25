"""
Pydantic схемы для ответов на опросы
"""
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime


class ResponseCreate(BaseModel):
    """Схема для создания ответа"""
    quiz_id: int
    answers: Dict[str, Any]


class ResponseResponse(BaseModel):
    """Схема ответа с данными"""
    id: int
    quiz_id: int
    user_id: int
    answers: Dict[str, Any]
    completed_at: datetime

    class Config:
        from_attributes = True


class ResponseWithUserResponse(ResponseResponse):
    """Схема ответа с данными пользователя"""
    telegram_id: int
    username: str | None
    first_name: str | None
    email: str | None


class ResponseListResponse(BaseModel):
    """Схема списка ответов"""
    responses: list[ResponseWithUserResponse]
    total: int


class ResponseSubmit(BaseModel):
    """Схема для отправки ответа"""
    quiz_id: int
    answers: Dict[str, Any]


class ResponseSubmitResponse(BaseModel):
    """Схема ответа после отправки"""
    message: str
    response_id: int
