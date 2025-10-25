# 📊 Визуальный Конструктор Опросов (Telegram Mini App)

Полнофункциональный сервис для создания, проведения и анализа опросов в Telegram.

## 🚀 Возможности

- **Визуальный конструктор** опросов с drag-and-drop интерфейсом
- **Условная логика** переходов между вопросами
- **Различные типы вопросов**: текст, выбор, шкала, загрузка файлов
- **Аналитика в реальном времени** с графиками и диаграммами
- **Экспорт данных** в CSV/Excel
- **Управление администраторами** и пользователями
- **Настраиваемый онбординг** (сбор имени, email, телефона)
- **Брендирование** (цвета, логотип)

## 🛠 Технологический Стек

- **Backend**: Python (aiogram, FastAPI)
- **Frontend**: React + Material UI
- **Database**: PostgreSQL
- **Deployment**: Docker + Docker Compose

## 📦 Установка и Запуск

### Предварительные требования

- Docker и Docker Compose
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))

### Шаг 1: Клонирование репозитория

```bash
git clone <repository-url>
cd oprosy
```

### Шаг 2: Настройка переменных окружения

```bash
cp .env.example .env
nano .env  # Отредактируйте файл, добавьте свои значения
```

**Обязательно укажите:**
- `BOT_TOKEN` - токен вашего бота
- `SUPERADMIN_ID` - ваш Telegram ID
- `DB_PASSWORD` - пароль для PostgreSQL
- `API_SECRET_KEY` - секретный ключ для API

### Шаг 3: Запуск через Docker Compose

```bash
docker-compose up -d --build
```

Сервисы будут доступны:
- **Bot**: автоматически подключится к Telegram
- **API**: http://localhost:8000
- **WebApp**: http://localhost:3000
- **PostgreSQL**: localhost:5432

### Шаг 4: Применение миграций БД

```bash
docker-compose exec api alembic upgrade head
```

### Шаг 5: Проверка работы

Откройте Telegram и напишите боту `/start`

## 📁 Структура Проекта

```
oprosy/
├── bot/                    # Telegram бот (aiogram)
│   ├── handlers/          # Обработчики команд
│   ├── keyboards/         # Клавиатуры
│   ├── middlewares/       # Middleware
│   ├── utils/             # Утилиты
│   └── main.py           # Точка входа бота
├── api/                   # REST API (FastAPI)
│   ├── routes/           # Endpoints
│   ├── models/           # SQLAlchemy модели
│   ├── schemas/          # Pydantic схемы
│   ├── services/         # Бизнес-логика
│   └── main.py          # Точка входа API
├── webapp/               # React фронтенд
│   ├── src/
│   │   ├── components/  # React компоненты
│   │   ├── pages/       # Страницы
│   │   └── services/    # API клиенты
│   └── public/
├── database/
│   ├── migrations/      # Alembic миграции
│   └── init.sql        # Начальная схема
├── uploads/            # Загруженные файлы
└── docker-compose.yml  # Docker конфигурация
```

## 🔧 Разработка

### Локальный запуск без Docker

#### Backend (Bot + API)

```bash
# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt

# Запустить бота
python bot/main.py

# Запустить API (в отдельном терминале)
uvicorn api.main:app --reload --port 8000
```

#### Frontend (React)

```bash
cd webapp
npm install
npm start
```

### База данных

```bash
# Создать новую миграцию
docker-compose exec api alembic revision --autogenerate -m "description"

# Применить миграции
docker-compose exec api alembic upgrade head

# Откатить миграцию
docker-compose exec api alembic downgrade -1
```

## 📚 API Документация

После запуска API, документация доступна по адресу:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔐 Безопасность

- Все запросы от WebApp валидируются через `initData`
- Rate limiting: 10 запросов в минуту на пользователя
- Файлы проверяются на тип и размер
- SQL injection защита через SQLAlchemy ORM
- CORS настроен только для доверенных источников

## 📊 Архитектура

```
Telegram Client
      ↓
   Bot (aiogram) ←→ PostgreSQL
      ↓                 ↑
   WebApp (React) → API (FastAPI)
```

## 🤝 Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose logs -f`
2. Убедитесь, что все переменные окружения заданы
3. Проверьте, что порты не заняты другими приложами

## 📝 Лицензия

Проект продается с исходным кодом. Все права принадлежат покупателю.

## 🎯 Roadmap

- [ ] Поддержка нескольких языков
- [ ] Интеграция с внешними сервисами (Google Sheets, Zapier)
- [ ] Расширенная аналитика с AI-инсайтами
- [ ] Мобильное приложение (iOS/Android)
