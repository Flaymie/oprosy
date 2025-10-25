"""
Endpoints для управления пользователями
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.database import get_db
from api.dependencies import get_current_admin
from api.schemas.user import UserResponse, UserListResponse
from database.models import User
from api.config import settings
import os

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=UserListResponse)
async def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Получить список всех пользователей
    
    Только для главного администратора (superadmin)
    """
    # Проверяем, является ли пользователь суперадмином
    superadmin_id = int(os.getenv("SUPERADMIN_ID", "0"))
    
    if current_user.telegram_id != superadmin_id:
        raise HTTPException(
            status_code=403,
            detail="Only superadmin can access this endpoint"
        )
    
    users = db.query(User).order_by(User.created_at.desc()).all()
    
    return UserListResponse(
        users=users,
        total=len(users)
    )


@router.put("/{user_id}/admin", response_model=UserResponse)
async def set_admin_status(
    user_id: int,
    is_admin: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Изменить статус администратора пользователя
    
    Только для главного администратора (superadmin)
    """
    # Проверяем, является ли пользователь суперадмином
    superadmin_id = int(os.getenv("SUPERADMIN_ID", "0"))
    
    if current_user.telegram_id != superadmin_id:
        raise HTTPException(
            status_code=403,
            detail="Only superadmin can manage admin status"
        )
    
    # Находим пользователя
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Нельзя изменить статус суперадмина
    if user.telegram_id == superadmin_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot change superadmin status"
        )
    
    # Обновляем статус
    user.is_admin = is_admin
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Получить информацию о текущем пользователе
    """
    return current_user
