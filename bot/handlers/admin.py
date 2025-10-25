"""
Обработчики команд администратора
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from utils.database import Database
from keyboards.inline import get_admin_panel_keyboard
from config import Config

router = Router()


@router.message(Command("admin"))
async def cmd_admin(message: Message, db: Database, config: Config):
    """
    Обработчик команды /admin
    Открывает админ-панель для авторизованных администраторов
    """
    telegram_id = message.from_user.id
    
    # Проверяем права администратора
    is_superadmin = telegram_id == config.superadmin_id
    is_admin = await db.is_admin(telegram_id)
    
    if not (is_superadmin or is_admin):
        await message.answer(
            "❌ У вас нет прав администратора.\n\n"
            "Для получения доступа обратитесь к главному администратору."
        )
        return
    
    # Отправляем кнопку для открытия админ-панели
    await message.answer(
        "📊 <b>Админ-панель</b>\n\n"
        f"{'🔑 Вы вошли как главный администратор.' if is_superadmin else '👤 Вы вошли как администратор.'}\n\n"
        "Доступные функции:\n"
        "• Создание и редактирование опросов\n"
        "• Просмотр аналитики и результатов\n"
        "• Экспорт данных в CSV/Excel\n"
        f"{'• Управление администраторами' if is_superadmin else ''}\n\n"
        "Нажмите на кнопку ниже для открытия панели управления.",
        reply_markup=get_admin_panel_keyboard(config.webapp_url),
        parse_mode="HTML"
    )


@router.message(Command("stats"))
async def cmd_stats(message: Message, db: Database, config: Config):
    """
    Статистика для администратора
    """
    telegram_id = message.from_user.id
    
    # Проверяем права администратора
    is_admin = await db.is_admin(telegram_id) or telegram_id == config.superadmin_id
    
    if not is_admin:
        await message.answer("❌ У вас нет прав администратора.")
        return
    
    # Получаем пользователя из БД
    user = await db.get_user_by_telegram_id(telegram_id)
    if not user:
        await message.answer("❌ Ошибка: пользователь не найден в базе данных.")
        return
    
    user_id = user['id']
    
    # Получаем статистику
    quizzes = await db.get_quizzes_by_creator(user_id)
    total_quizzes = len(quizzes)
    
    active_quizzes = len([q for q in quizzes if q['status'] == 'active'])
    draft_quizzes = len([q for q in quizzes if q['status'] == 'draft'])
    archived_quizzes = len([q for q in quizzes if q['status'] == 'archived'])
    
    # Подсчитываем общее количество ответов
    total_responses = 0
    for quiz in quizzes:
        responses = await db.get_responses_by_quiz(quiz['id'])
        total_responses += len(responses)
    
    await message.answer(
        f"📊 <b>Статистика</b>\n\n"
        f"📝 Всего опросов: {total_quizzes}\n"
        f"✅ Активных: {active_quizzes}\n"
        f"📄 Черновиков: {draft_quizzes}\n"
        f"🗄 Архивных: {archived_quizzes}\n\n"
        f"💬 Всего ответов: {total_responses}\n\n"
        f"Для подробной аналитики используйте /admin",
        parse_mode="HTML"
    )
