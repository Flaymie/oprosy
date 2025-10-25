"""
Утилиты для работы с базой данных
"""
import asyncpg
from typing import Optional, Dict, Any, List
from config import DatabaseConfig


class Database:
    """Класс для работы с PostgreSQL"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Создает пул подключений к базе данных"""
        self.pool = await asyncpg.create_pool(
            host=self.config.host,
            port=self.config.port,
            database=self.config.name,
            user=self.config.user,
            password=self.config.password,
            min_size=5,
            max_size=20
        )

    async def disconnect(self):
        """Закрывает пул подключений"""
        if self.pool:
            await self.pool.close()

    # ==================== USERS ====================

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Получить пользователя по Telegram ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE telegram_id = $1",
                telegram_id
            )
            return dict(row) if row else None

    async def create_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """Создать нового пользователя"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO users (telegram_id, username, first_name, last_name, email, phone)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
                """,
                telegram_id, username, first_name, last_name, email, phone
            )
            return dict(row)

    async def update_user(
        self,
        telegram_id: int,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Обновить данные пользователя"""
        if not kwargs:
            return None

        fields = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(kwargs.keys())])
        values = [telegram_id] + list(kwargs.values())

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                f"UPDATE users SET {fields} WHERE telegram_id = $1 RETURNING *",
                *values
            )
            return dict(row) if row else None

    async def is_admin(self, telegram_id: int) -> bool:
        """Проверить, является ли пользователь администратором"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT is_admin FROM users WHERE telegram_id = $1",
                telegram_id
            )
            return result or False

    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Получить всех пользователей"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM users ORDER BY created_at DESC")
            return [dict(row) for row in rows]

    async def set_admin_status(self, user_id: int, is_admin: bool) -> bool:
        """Установить статус администратора"""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "UPDATE users SET is_admin = $1 WHERE id = $2",
                is_admin, user_id
            )
            return result == "UPDATE 1"

    # ==================== QUIZZES ====================

    async def get_quiz_by_id(self, quiz_id: int) -> Optional[Dict[str, Any]]:
        """Получить опрос по ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM quizzes WHERE id = $1",
                quiz_id
            )
            return dict(row) if row else None

    async def get_quizzes_by_creator(self, creator_id: int) -> List[Dict[str, Any]]:
        """Получить все опросы созданные пользователем"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM quizzes WHERE creator_id = $1 ORDER BY created_at DESC",
                creator_id
            )
            return [dict(row) for row in rows]

    async def create_quiz(
        self,
        creator_id: int,
        title: str,
        description: str = "",
        structure: Dict = None,
        settings: Dict = None,
        status: str = "draft"
    ) -> Dict[str, Any]:
        """Создать новый опрос"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO quizzes (creator_id, title, description, structure, settings, status)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
                """,
                creator_id, title, description, structure or {}, settings or {}, status
            )
            return dict(row)

    async def update_quiz(self, quiz_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Обновить опрос"""
        if not kwargs:
            return None

        fields = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(kwargs.keys())])
        values = [quiz_id] + list(kwargs.values())

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                f"UPDATE quizzes SET {fields} WHERE id = $1 RETURNING *",
                *values
            )
            return dict(row) if row else None

    async def delete_quiz(self, quiz_id: int) -> bool:
        """Удалить опрос"""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM quizzes WHERE id = $1",
                quiz_id
            )
            return result == "DELETE 1"

    # ==================== RESPONSES ====================

    async def create_response(
        self,
        quiz_id: int,
        user_id: int,
        answers: Dict
    ) -> Optional[Dict[str, Any]]:
        """Сохранить ответы пользователя"""
        async with self.pool.acquire() as conn:
            try:
                row = await conn.fetchrow(
                    """
                    INSERT INTO responses (quiz_id, user_id, answers)
                    VALUES ($1, $2, $3)
                    RETURNING *
                    """,
                    quiz_id, user_id, answers
                )
                return dict(row) if row else None
            except asyncpg.UniqueViolationError:
                # Пользователь уже проходил этот опрос
                return None

    async def get_responses_by_quiz(self, quiz_id: int) -> List[Dict[str, Any]]:
        """Получить все ответы по опросу"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT r.*, u.telegram_id, u.username, u.first_name, u.email
                FROM responses r
                JOIN users u ON r.user_id = u.id
                WHERE r.quiz_id = $1
                ORDER BY r.completed_at DESC
                """,
                quiz_id
            )
            return [dict(row) for row in rows]

    async def has_user_completed_quiz(self, quiz_id: int, user_id: int) -> bool:
        """Проверить, проходил ли пользователь опрос"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM responses WHERE quiz_id = $1 AND user_id = $2)",
                quiz_id, user_id
            )
            return result

    # ==================== FILES ====================

    async def create_file(
        self,
        user_id: int,
        file_path: str,
        file_type: str,
        file_size: int,
        quiz_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Сохранить метаданные файла"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO files (quiz_id, user_id, file_path, file_type, file_size)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
                """,
                quiz_id, user_id, file_path, file_type, file_size
            )
            return dict(row)

    async def get_files_by_quiz(self, quiz_id: int) -> List[Dict[str, Any]]:
        """Получить все файлы по опросу"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM files WHERE quiz_id = $1 ORDER BY uploaded_at DESC",
                quiz_id
            )
            return [dict(row) for row in rows]
