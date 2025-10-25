"""
Endpoints для управления опросами
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from api.database import get_db
from api.dependencies import get_current_user, get_current_admin
from api.schemas.quiz import QuizCreate, QuizUpdate, QuizResponse, QuizListResponse, QuizStatsResponse
from database.models import User, Quiz, Response

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.get("", response_model=QuizListResponse)
async def get_quizzes(
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Получить список всех опросов текущего администратора
    
    Опционально фильтровать по статусу: draft, active, archived
    """
    query = db.query(Quiz).filter(Quiz.creator_id == current_user.id)
    
    if status:
        query = query.filter(Quiz.status == status)
    
    quizzes = query.order_by(Quiz.created_at.desc()).all()
    
    return QuizListResponse(
        quizzes=quizzes,
        total=len(quizzes)
    )


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить опрос по ID
    
    Администраторы видят свои опросы, пользователи - только активные
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Проверка прав доступа
    if not current_user.is_admin:
        # Обычные пользователи видят только активные опросы
        if quiz.status != "active":
            raise HTTPException(status_code=403, detail="Access denied")
    else:
        # Администраторы видят только свои опросы
        if quiz.creator_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return quiz


@router.post("", response_model=QuizResponse, status_code=201)
async def create_quiz(
    quiz_data: QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Создать новый опрос
    
    Только для администраторов
    """
    new_quiz = Quiz(
        creator_id=current_user.id,
        title=quiz_data.title,
        description=quiz_data.description,
        structure=quiz_data.structure,
        settings=quiz_data.settings,
        status=quiz_data.status
    )
    
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)
    
    return new_quiz


@router.put("/{quiz_id}", response_model=QuizResponse)
async def update_quiz(
    quiz_id: int,
    quiz_data: QuizUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Обновить опрос
    
    Только создатель опроса может его редактировать
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Обновляем только переданные поля
    update_data = quiz_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(quiz, field, value)
    
    db.commit()
    db.refresh(quiz)
    
    return quiz


@router.delete("/{quiz_id}", status_code=204)
async def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Удалить опрос
    
    Только создатель опроса может его удалить
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db.delete(quiz)
    db.commit()
    
    return None


@router.get("/{quiz_id}/stats", response_model=QuizStatsResponse)
async def get_quiz_stats(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Получить статистику опроса
    
    Только для создателя опроса
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Подсчитываем количество ответов
    total_responses = db.query(Response).filter(Response.quiz_id == quiz_id).count()
    
    return QuizStatsResponse(
        quiz_id=quiz.id,
        title=quiz.title,
        total_responses=total_responses,
        status=quiz.status,
        created_at=quiz.created_at
    )
