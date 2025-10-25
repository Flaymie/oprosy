"""
Pydantic схемы для опросов
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class QuizBase(BaseModel):
    """Базовая схема опроса"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    structure: Dict[str, Any] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="draft", pattern="^(draft|active|archived)$")


class QuizCreate(QuizBase):
    """Схема для создания опроса"""
    pass


class QuizUpdate(BaseModel):
    """Схема для обновления опроса"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    structure: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, pattern="^(draft|active|archived)$")


class QuizResponse(QuizBase):
    """Схема ответа с данными опроса"""
    id: int
    creator_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuizListResponse(BaseModel):
    """Схема списка опросов"""
    quizzes: list[QuizResponse]
    total: int


class QuizStatsResponse(BaseModel):
    """Схема статистики опроса"""
    quiz_id: int
    title: str
    total_responses: int
    status: str
    created_at: datetime
