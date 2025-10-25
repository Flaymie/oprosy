"""
Фикс для is_admin NULL в БД
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy import create_engine, text
from api.config import settings

# Подключаемся к БД
engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    # Обновляем NULL на FALSE
    result = conn.execute(text("UPDATE users SET is_admin = FALSE WHERE is_admin IS NULL"))
    conn.commit()
    print(f"✅ Обновлено {result.rowcount} пользователей")

print("✅ Готово!")
