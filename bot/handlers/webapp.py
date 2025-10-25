"""
Обработчики данных от WebApp
"""
import json
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Filter

from utils.database import Database
from config import Config

router = Router()


class WebAppDataFilter(Filter):
    """Фильтр для сообщений с web_app_data"""
    
    async def __call__(self, message: Message) -> bool:
        return message.web_app_data is not None


@router.message(WebAppDataFilter())
async def handle_webapp_data(message: Message, db: Database, config: Config):
    """
    Обработчик данных от WebApp
    Принимает финальные команды от фронтенда
    """
    try:
        # Парсим данные от WebApp
        data = json.loads(message.web_app_data.data)
        command = data.get("command")
        
        if command == "finish_quiz":
            # Пользователь завершил опрос
            quiz_id = data.get("quiz_id")
            
            await message.answer(
                "✅ Спасибо за прохождение опроса!\n\n"
                "Ваши ответы сохранены.",
                reply_markup=message.reply_markup
            )
            
            # Уведомляем создателя опроса
            quiz = await db.get_quiz_by_id(quiz_id)
            if quiz:
                creator_id = quiz['creator_id']
        
        elif command == "close_webapp":
            # Просто закрываем WebApp
            await message.answer("👋 До встречи!")
        
        else:
            # Неизвестная команда
            await message.answer("✅ Действие выполнено.")
    
    except json.JSONDecodeError:
        await message.answer("❌ Ошибка обработки данных.")
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {str(e)}")
