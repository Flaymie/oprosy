"""
Endpoints для аутентификации
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas.auth import InitDataValidation, AuthResponse
from api.utils.auth import validate_init_data
from database.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/validate", response_model=AuthResponse)
async def validate_init_data_endpoint(
    data: InitDataValidation,
    db: Session = Depends(get_db)
):
    """
    Валидация initData от Telegram WebApp
    
    Проверяет подпись и возвращает данные пользователя
    """
    # Валидируем initData
    user_data = validate_init_data(data.init_data)
    
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid initData signature or expired"
        )
    
    telegram_id = user_data['telegram_id']
    
    # Ищем пользователя в БД
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found. Please start the bot first."
        )
    
    return AuthResponse(
        user_id=user.id,
        telegram_id=user.telegram_id,
        is_admin=user.is_admin,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
