"""
Подключение к базе данных для API
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session

from config import settings

# Синхронный движок (для обычных операций)
engine = create_engine(settings.database_url, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Асинхронный движок (для асинхронных операций) - опционально
try:
    async_engine = create_async_engine(settings.async_database_url, echo=False, pool_pre_ping=True)
    AsyncSessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
except ImportError:
    # asyncpg не установлен, пропускаем асинхронный движок
    async_engine = None
    AsyncSessionLocal = None


def get_db() -> Session:
    """Dependency для получения синхронной сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncSession:
    """Dependency для получения асинхронной сессии БД"""
    async with AsyncSessionLocal() as session:
        yield session
