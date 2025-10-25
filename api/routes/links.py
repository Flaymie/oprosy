"""
Endpoints для управления ссылками на опросы
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from database import get_db
from dependencies import get_current_admin
from database.models import User, Quiz, QuizLink

router = APIRouter(prefix="/links", tags=["Links"])


@router.post("/quiz/{quiz_id}")
async def create_quiz_link(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Создать новую ссылку на опрос с уникальным UUID
    
    Только создатель опроса может создавать ссылки
    """
    # Проверяем существование опроса
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Генерируем UUID
    link_uuid = str(uuid.uuid4())
    
    # Создаем ссылку
    new_link = QuizLink(
        quiz_id=quiz_id,
        link_uuid=link_uuid,
        is_active=True,
        created_by=current_user.id
    )
    
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    
    return {
        "id": new_link.id,
        "quiz_id": new_link.quiz_id,
        "link_uuid": new_link.link_uuid,
        "is_active": new_link.is_active,
        "created_at": new_link.created_at
    }


@router.get("/quiz/{quiz_id}")
async def get_quiz_links(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Получить все ссылки для опроса
    
    Только создатель опроса может видеть ссылки
    """
    # Проверяем существование опроса
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Получаем все ссылки
    links = db.query(QuizLink).filter(QuizLink.quiz_id == quiz_id).all()
    
    return {
        "links": [
            {
                "id": link.id,
                "quiz_id": link.quiz_id,
                "link_uuid": link.link_uuid,
                "is_active": link.is_active,
                "created_at": link.created_at
            }
            for link in links
        ]
    }


@router.get("/resolve/{link_uuid}")
async def resolve_link(
    link_uuid: str,
    db: Session = Depends(get_db)
):
    """
    Получить информацию об опросе по UUID ссылки
    
    Публичный endpoint - не требует авторизации
    """
    try:
        link = db.query(QuizLink).filter(
            QuizLink.link_uuid == link_uuid,
            QuizLink.is_active == True
        ).first()
        
        if not link:
            raise HTTPException(status_code=404, detail="Link not found or inactive")
        
        quiz = db.query(Quiz).filter(Quiz.id == link.quiz_id).first()
        
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Возвращаем quiz_id даже если опрос не активен - пусть фронт решает
        return {
            "quiz_id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "status": quiz.status
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{link_id}")
async def delete_link(
    link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Удалить (деактивировать) ссылку
    
    Только создатель опроса может удалять ссылки
    """
    link = db.query(QuizLink).filter(QuizLink.id == link_id).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    quiz = db.query(Quiz).filter(Quiz.id == link.quiz_id).first()
    
    if quiz.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Деактивируем ссылку вместо удаления
    link.is_active = False
    db.commit()
    
    return {"message": "Link deactivated successfully"}
