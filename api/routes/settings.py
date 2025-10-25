"""
Endpoints для управления настройками
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from dependencies import get_current_admin

router = APIRouter(prefix="/settings", tags=["Settings"])


class SettingsModel(BaseModel):
    collectPhone: bool = False
    collectEmail: bool = False
    collectUsername: bool = True
    collectFirstName: bool = True
    collectLastName: bool = False


# Временное хранилище настроек (в продакшене - БД)
_settings_storage = SettingsModel()


@router.get("")
async def get_settings(
    current_user = Depends(get_current_admin)
):
    """
    Получить текущие настройки сбора контактов
    """
    return _settings_storage.dict()


@router.post("")
async def save_settings(
    settings: SettingsModel,
    current_user = Depends(get_current_admin)
):
    """
    Сохранить настройки сбора контактов
    """
    global _settings_storage
    _settings_storage = settings
    
    return {"message": "Settings saved successfully"}
