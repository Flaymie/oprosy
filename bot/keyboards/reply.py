"""
Reply клавиатуры для бота
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo


def get_main_menu_keyboard(is_admin: bool = False, webapp_url: str = "") -> ReplyKeyboardMarkup:
    """
    Главное меню бота
    
    Args:
        is_admin: Является ли пользователь администратором
        webapp_url: URL WebApp
    """
    buttons = []
    
    if is_admin and webapp_url:
        buttons.append([
            KeyboardButton(
                text="📊 Админ-панель",
                web_app=WebAppInfo(url=f"{webapp_url}/admin")
            )
        ])
    
    buttons.append([KeyboardButton(text="ℹ️ О боте")])
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )


def get_onboarding_keyboard(require_name: bool = False, require_email: bool = False, require_phone: bool = False) -> ReplyKeyboardMarkup:
    """
    Клавиатура для онбординга
    
    Args:
        require_name: Требуется ли имя
        require_email: Требуется ли email
        require_phone: Требуется ли телефон
    """
    buttons = []
    
    if require_phone:
        buttons.append([
            KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)
        ])
    
    if require_name:
        buttons.append([KeyboardButton(text="✏️ Ввести имя")])
    
    if require_email:
        buttons.append([KeyboardButton(text="📧 Ввести email")])
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Заполните данные..."
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
