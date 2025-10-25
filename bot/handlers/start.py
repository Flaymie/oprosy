"""
Обработчик команды /start и онбординга
"""
from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.database import Database
from keyboards.reply import get_main_menu_keyboard, get_onboarding_keyboard, get_cancel_keyboard
from config import Config

router = Router()


class OnboardingStates(StatesGroup):
    """Состояния для процесса онбординга"""
    waiting_for_name = State()
    waiting_for_email = State()
    waiting_for_phone = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db: Database, config: Config):
    """
    Обработчик команды /start
    Проверяет наличие пользователя в БД и запускает онбординг при необходимости
    Поддерживает deep linking для открытия конкретного опроса: /start quiz_123
    """
    telegram_id = message.from_user.id
    
    # Получаем параметр из deep link (например, 123 - это quiz_id)
    args = message.text.split(maxsplit=1)
    quiz_id = args[1] if len(args) > 1 else None
    
    # Проверяем, есть ли пользователь в БД
    user = await db.get_user_by_telegram_id(telegram_id)
    
    
    if user:
        # Пользователь уже зарегистрирован
        is_admin = user.get('is_admin', False) or telegram_id == config.superadmin_id
        
        # Если есть quiz_id - СРАЗУ открываем WebApp
        if quiz_id:
            webapp_url = f"{config.webapp_url}/quiz/{quiz_id}"
            
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📝 Пройти опрос", web_app=WebAppInfo(url=webapp_url))]
            ])
            
            await message.answer(
                "📝 Опрос",
                reply_markup=keyboard
            )
        else:
            await message.answer(
                f"👋 С возвращением, {user.get('first_name', 'пользователь')}!\n\n"
                "Используйте меню ниже для навигации.",
                reply_markup=get_main_menu_keyboard(is_admin, config.webapp_url)
            )
    else:
        # Новый пользователь - создаем с базовыми данными
        await db.create_user(
            telegram_id=telegram_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        # Проверяем, является ли пользователь суперадмином
        is_superadmin = telegram_id == config.superadmin_id
        if is_superadmin:
            await db.update_user(telegram_id, is_admin=True)
        
        is_admin = is_superadmin
        
        # Если есть quiz_id - СРАЗУ открываем WebApp
        if quiz_id:
            webapp_url = f"{config.webapp_url}/quiz/{quiz_id}"
            
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📝 Пройти опрос", web_app=WebAppInfo(url=webapp_url))]
            ])
            
            await message.answer(
                "📝 Опрос",
                reply_markup=keyboard
            )
        else:
            await message.answer(
                "👋 Добро пожаловать!\n\n"
                "Я бот для создания и проведения опросов.\n\n"
                f"{'🔑 Вы вошли как администратор.' if is_admin else 'Вы можете проходить опросы, созданные администраторами.'}",
                reply_markup=get_main_menu_keyboard(is_admin, config.webapp_url)
            )


@router.message(F.text == "ℹ️ О боте")
async def about_bot(message: Message):
    """Информация о боте"""
    await message.answer(
        "📊 <b>Визуальный Конструктор Опросов</b>\n\n"
        "Этот бот позволяет:\n"
        "• Создавать сложные опросы с условной логикой\n"
        "• Проходить опросы в удобном интерфейсе\n"
        "• Анализировать результаты в реальном времени\n"
        "• Экспортировать данные в CSV/Excel\n\n"
        "Разработано с использованием современных технологий:\n"
        "Python (aiogram, FastAPI) + React + PostgreSQL",
        parse_mode="HTML"
    )


@router.message(F.text == "📊 Админ-панель")
async def admin_panel_text(message: Message, db: Database, config: Config):
    """Обработчик текстовой кнопки админ-панели"""
    telegram_id = message.from_user.id
    
    # Проверяем права администратора
    is_admin = await db.is_admin(telegram_id) or telegram_id == config.superadmin_id
    
    if not is_admin:
        await message.answer("❌ У вас нет прав администратора.")
        return
    
    await message.answer(
        "📊 <b>Админ-панель</b>\n\n"
        "Нажмите на кнопку выше для открытия панели управления.",
        parse_mode="HTML"
    )


# ==================== ОНБОРДИНГ ====================
# Эти обработчики будут использоваться для сбора данных при необходимости

@router.message(StateFilter(OnboardingStates.waiting_for_name))
async def process_name(message: Message, state: FSMContext, db: Database):
    """Обработка ввода имени"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "Регистрация отменена.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    # Сохраняем имя
    telegram_id = message.from_user.id
    await db.update_user(telegram_id, first_name=message.text)
    
    await state.clear()
    await message.answer(
        "✅ Имя сохранено!",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(StateFilter(OnboardingStates.waiting_for_email))
async def process_email(message: Message, state: FSMContext, db: Database):
    """Обработка ввода email"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "Ввод email отменен.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    # Простая валидация email
    if "@" not in message.text or "." not in message.text:
        await message.answer("❌ Некорректный email. Попробуйте еще раз.")
        return
    
    # Сохраняем email
    telegram_id = message.from_user.id
    await db.update_user(telegram_id, email=message.text)
    
    await state.clear()
    await message.answer(
        "✅ Email сохранен!",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(StateFilter(OnboardingStates.waiting_for_phone), F.contact)
async def process_phone_contact(message: Message, state: FSMContext, db: Database):
    """Обработка отправки контакта с номером телефона"""
    phone = message.contact.phone_number
    
    # Сохраняем телефон
    telegram_id = message.from_user.id
    await db.update_user(telegram_id, phone=phone)
    
    await state.clear()
    await message.answer(
        "✅ Номер телефона сохранен!",
        reply_markup=ReplyKeyboardRemove()
    )
