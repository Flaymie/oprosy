"""
Утилиты для аутентификации и валидации Telegram WebApp initData
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import hmac
import hashlib
from urllib.parse import parse_qsl
from typing import Dict, Optional
import json

from config import settings


def validate_init_data(init_data: str) -> Optional[Dict]:
    """
    Валидация initData от Telegram WebApp
    
    Args:
        init_data: Строка initData от Telegram
        
    Returns:
        Dict с данными пользователя или None если валидация не прошла
    """
    try:
        # Парсим init_data
        parsed_data = dict(parse_qsl(init_data))
        
        # Извлекаем hash
        received_hash = parsed_data.pop('hash', None)
        if not received_hash:
            return None
        
        # Создаем data_check_string
        data_check_arr = [f"{key}={value}" for key, value in sorted(parsed_data.items())]
        data_check_string = '\n'.join(data_check_arr)
        
        # Создаем secret_key
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=settings.BOT_TOKEN.encode(),
            digestmod=hashlib.sha256
        ).digest()
        
        # Вычисляем hash
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # Сравниваем хеши
        if calculated_hash != received_hash:
            return None
        
        # Проверяем auth_date (не старше 24 часов)
        import time
        auth_date = int(parsed_data.get('auth_date', 0))
        current_time = int(time.time())
        
        if current_time - auth_date > 86400:  # 24 часа
            return None
        
        # Извлекаем данные пользователя
        user_data = json.loads(parsed_data.get('user', '{}'))
        
        return {
            'telegram_id': user_data.get('id'),
            'username': user_data.get('username'),
            'first_name': user_data.get('first_name'),
            'last_name': user_data.get('last_name'),
            'language_code': user_data.get('language_code'),
            'auth_date': auth_date
        }
        
    except Exception as e:
        print(f"Error validating init_data: {e}")
        return None


def extract_user_from_init_data(init_data: str) -> Optional[int]:
    """
    Извлекает telegram_id из initData без полной валидации
    Используется для быстрой проверки
    
    Args:
        init_data: Строка initData от Telegram
        
    Returns:
        telegram_id или None
    """
    try:
        parsed_data = dict(parse_qsl(init_data))
        user_data = json.loads(parsed_data.get('user', '{}'))
        return user_data.get('id')
    except:
        return None
