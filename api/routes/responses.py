"""
Endpoints для работы с ответами на опросы
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from api.database import get_db
from api.dependencies import get_current_user, get_current_admin
from api.schemas.response import ResponseCreate, ResponseResponse, ResponseListResponse, ResponseWithUserResponse, ResponseSubmit, ResponseSubmitResponse
from database.models import User, Quiz, Response

router = APIRouter(prefix="/responses", tags=["Responses"])


@router.post("", response_model=ResponseSubmitResponse)
async def submit_response(
    response_data: ResponseSubmit,
    db: Session = Depends(get_db)
):
    """
    Сохранить ответы пользователя на опрос
    
    Пользователь может пройти опрос только один раз
    """
    # Проверяем существование опроса
    quiz = db.query(Quiz).filter(Quiz.id == response_data.quiz_id).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Проверяем, что опрос активен
    if quiz.status != "active":
        raise HTTPException(status_code=400, detail="Quiz is not active")
    
    new_response = Response(
        quiz_id=response_data.quiz_id,
        user_id=None,
        answers=response_data.answers
    )
    
    try:
        db.add(new_response)
        db.commit()
        db.refresh(new_response)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Failed to save response. You may have already completed this quiz."
        )
    
    return new_response


@router.get("/{quiz_id}", response_model=ResponseListResponse)
async def get_responses(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Получить все ответы по опросу
    
    Только для создателя опроса
    """
    # Проверяем существование опроса
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Проверяем права доступа
    if quiz.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Получаем все ответы с данными пользователей
    responses = db.query(
        Response,
        User.telegram_id,
        User.username,
        User.first_name,
        User.email
    ).join(
        User, Response.user_id == User.id
    ).filter(
        Response.quiz_id == quiz_id
    ).order_by(
        Response.completed_at.desc()
    ).all()
    
    # Формируем ответ
    response_list = []
    for resp, telegram_id, username, first_name, email in responses:
        response_list.append(
            ResponseWithUserResponse(
                id=resp.id,
                quiz_id=resp.quiz_id,
                user_id=resp.user_id,
                answers=resp.answers,
                completed_at=resp.completed_at,
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                email=email
            )
        )
    
    return ResponseListResponse(
        responses=response_list,
        total=len(response_list)
    )


@router.get("/my/{quiz_id}", response_model=ResponseResponse)
async def get_my_response(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить свой ответ на опрос
    
    Для проверки, проходил ли пользователь опрос
    """
    response = db.query(Response).filter(
        Response.quiz_id == quiz_id,
        Response.user_id == current_user.id
    ).first()
    
    if not response:
        raise HTTPException(
            status_code=404,
            detail="You haven't completed this quiz yet"
        )
    
    return response
