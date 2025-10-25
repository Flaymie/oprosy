"""
SQLAlchemy модели для Alembic миграций
"""
from sqlalchemy import Column, Integer, BigInteger, String, Text, Boolean, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """Модель пользователя"""
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    is_admin = Column(Boolean, default=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class Quiz(Base):
    """Модель опроса"""
    __tablename__ = 'quizzes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    creator_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    structure = Column(JSONB, nullable=False, default={})
    settings = Column(JSONB, nullable=False, default={})
    status = Column(String(20), nullable=False, default='draft', index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("status IN ('draft', 'active', 'archived')", name='check_quiz_status'),
    )


class QuizLink(Base):
    """Модель ссылки на опрос с UUID"""
    __tablename__ = 'quiz_links'

    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False, index=True)
    link_uuid = Column(String(36), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    created_by = Column(BigInteger, ForeignKey('users.id', ondelete='SET NULL'))


class Response(Base):
    """Модель ответа на опрос"""
    __tablename__ = 'responses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    answers = Column(JSONB, nullable=False, default={})
    completed_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        # Уникальная пара quiz_id + user_id (один пользователь - один ответ на опрос)
        {'sqlite_autoincrement': True},
    )


class File(Base):
    """Модель файла"""
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey('quizzes.id', ondelete='CASCADE'), index=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    uploaded_at = Column(TIMESTAMP, server_default=func.now())
