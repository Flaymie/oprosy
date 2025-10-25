"""
Dependencies для FastAPI endpoints
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional

from api.database import get_db
from api.utils.auth import validate_init_data
from database.models import User


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency для получения текущего пользователя из initData
    
    Ожидает заголовок: Authorization: Bearer <initData>
    
    ДЛЯ РАЗРАБОТКИ: если нет authorization, возвращаем первого админа
    """
    # ДЛЯ РАЗРАБОТКИ: если нет authorization, берем первого админа
    if not authorization:
        # Ищем первого админа в БД
        admin_user = db.query(User).filter(User.is_admin == True).first()
        if admin_user:
            return admin_user
        
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )
    
    # Извлекаем initData из заголовка
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format"
        )
    
    init_data = authorization.replace("Bearer ", "")
    
    # Валидируем initData
    user_data = validate_init_data(init_data)
    
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid initData"
        )
    
    # Получаем пользователя из БД
    telegram_id = user_data.get('telegram_id')
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency для проверки прав администратора
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    return current_user
