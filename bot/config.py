"""
Конфигурация бота
"""
import os
from dataclasses import dataclass
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()


@dataclass
class DatabaseConfig:
    """Конфигурация базы данных"""
    host: str
    port: int
    name: str
    user: str
    password: str

    @property
    def url(self) -> str:
        """Возвращает URL для подключения к PostgreSQL"""
        # Экранируем спецсимволы в пароле
        password_encoded = quote_plus(self.password)
        return f"postgresql://{self.user}:{password_encoded}@{self.host}:{self.port}/{self.name}"

    @property
    def async_url(self) -> str:
        """Возвращает асинхронный URL для подключения к PostgreSQL"""
        # Экранируем спецсимволы в пароле
        password_encoded = quote_plus(self.password)
        return f"postgresql+asyncpg://{self.user}:{password_encoded}@{self.host}:{self.port}/{self.name}"


@dataclass
class Config:
    """Конфигурация приложения"""
    # Bot
    token: str
    superadmin_id: int
    
    # Database
    db: DatabaseConfig
    
    # WebApp
    webapp_url: str


def load_config() -> Config:
    """Загружает конфигурацию из переменных окружения"""
    return Config(
        token=os.getenv("BOT_TOKEN", ""),
        superadmin_id=int(os.getenv("SUPERADMIN_ID", "0")),
        db=DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            name=os.getenv("DB_NAME", "oprosy_db"),
            user=os.getenv("DB_USER", "oprosy_user"),
            password=os.getenv("DB_PASSWORD", "")
        ),
        webapp_url=os.getenv("WEBAPP_URL", "http://localhost:3000")
    )
