"""
Главный файл Telegram бота
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import load_config
from utils.database import Database
from handlers import start, admin, webapp

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""
    
    # Загружаем конфигурацию
    config = load_config()
    
    # Проверяем обязательные параметры
    if not config.token:
        logger.error("BOT_TOKEN не установлен в переменных окружения!")
        return
    
    if not config.superadmin_id:
        logger.error("SUPERADMIN_ID не установлен в переменных окружения!")
        return
    
    # Инициализируем бота
    bot = Bot(
        token=config.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Инициализируем диспетчер
    dp = Dispatcher()
    
    # Подключаемся к базе данных
    db = Database(config.db)
    await db.connect()
    logger.info("✅ Подключение к базе данных установлено")
    
    # Регистрируем роутеры
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(webapp.router)
    
    # Добавляем данные в контекст для всех хендлеров
    dp.workflow_data.update({
        "db": db,
        "config": config
    })
    
    # Запускаем бота
    logger.info("🚀 Бот запущен")
    logger.info(f"👤 Superadmin ID: {config.superadmin_id}")
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await db.disconnect()
        await bot.session.close()
        logger.info("👋 Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
