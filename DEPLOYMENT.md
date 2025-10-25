# 🚀 Deployment Guide

## Структура .env файлов

### 📁 `/api/.env`
```env
# DATABASE
DB_HOST=your_postgres_host
DB_PORT=5432
DB_NAME=oprosy_db
DB_USER=oprosy_user
DB_PASSWORD=your_secure_password

# API
API_SECRET_KEY=your_secret_key_min_32_chars

# FILES
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# RATE LIMITING
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_PERIOD=60
```

**Где деплоить:** Render, Railway, Heroku  
**URL пример:** `https://oprosy-api.onrender.com`

---

### 📁 `/bot/.env`
```env
# BOT
BOT_TOKEN=7786177639:AAH...
SUPERADMIN_ID=5170509558

# DATABASE (та же БД что и для API)
DB_HOST=your_postgres_host
DB_PORT=5432
DB_NAME=oprosy_db
DB_USER=oprosy_user
DB_PASSWORD=your_secure_password

# API (URL где задеплоен API)
API_HOST=https://oprosy-api.onrender.com

# WEBAPP (URL где задеплоен фронтенд)
WEBAPP_URL=https://oprosy-webapp.netlify.app
```

**Где деплоить:** Render, Railway, Heroku  
**Важно:** Должен работать 24/7 для polling

---

### 📁 `/webapp/.env`
```env
# API (URL где задеплоен API)
REACT_APP_API_URL=https://oprosy-api.onrender.com/api

# BOT
REACT_APP_BOT_USERNAME=musicvlkpyt_bot
```

**Где деплоить:** Netlify, Vercel  
**URL пример:** `https://oprosy-webapp.netlify.app`

---

## 🗄️ База данных

**Одна БД для всех сервисов!**

- API читает/пишет через SQLAlchemy
- Bot читает/пишет через asyncpg
- Можно использовать:
  - Render PostgreSQL (бесплатно)
  - Railway PostgreSQL
  - Supabase
  - Neon

**Настройки БД идут в:**
- `/api/.env` → `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `/bot/.env` → те же самые параметры

---

## 📝 Пошаговый деплой

### 1. База данных
1. Создай PostgreSQL на Render/Railway
2. Получи credentials (host, port, name, user, password)
3. Запусти миграции: `alembic upgrade head`

### 2. API
1. Деплой на Render/Railway
2. Добавь переменные из `/api/.env`
3. URL: `https://oprosy-api.onrender.com`

### 3. Bot
1. Деплой на Render/Railway
2. Добавь переменные из `/bot/.env`
3. Укажи `API_HOST` = URL API из шага 2
4. Укажи `WEBAPP_URL` = URL фронтенда (будет в шаге 4)

### 4. WebApp (Frontend)
1. Деплой на Netlify/Vercel
2. Добавь переменные из `/webapp/.env`
3. Укажи `REACT_APP_API_URL` = URL API из шага 2
4. URL: `https://oprosy-webapp.netlify.app`

### 5. Обновить Bot
1. Вернись к боту
2. Обнови `WEBAPP_URL` на URL из шага 4
3. Перезапусти бота

---

## ✅ Проверка

1. API: `https://oprosy-api.onrender.com/docs`
2. WebApp: `https://oprosy-webapp.netlify.app`
3. Bot: `/start` в Telegram

---

## 🔑 API_HOST vs WEBAPP_URL

- **API_HOST** = URL где живет API (бэкенд)
  - Пример: `https://oprosy-api.onrender.com`
  - Используется ботом для запросов к API

- **WEBAPP_URL** = URL где живет фронтенд (React)
  - Пример: `https://oprosy-webapp.netlify.app`
  - Используется ботом для открытия WebApp в Telegram
