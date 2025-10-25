"""
Inline клавиатуры для бота
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo


def get_quiz_keyboard(quiz_id: int, webapp_url: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для открытия опроса
    
    Args:
        quiz_id: ID опроса
        webapp_url: URL WebApp
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 Пройти опрос",
                    web_app=WebAppInfo(url=f"{webapp_url}/quiz/{quiz_id}")
                )
            ]
        ]
    )


def get_admin_panel_keyboard(webapp_url: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для открытия админ-панели
    
    Args:
        webapp_url: URL WebApp
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Открыть админ-панель",
                    web_app=WebAppInfo(url=f"{webapp_url}/admin")
                )
            ]
        ]
    )
