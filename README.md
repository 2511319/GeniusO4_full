# GeniusO4 - AI Crypto Analysis Platform

Платформа для профессионального анализа криптовалют с использованием ИИ, интегрированная с Telegram.

## Возможности

- 🤖 **Telegram Bot** - Получение анализа прямо в Telegram
- 🔐 **Telegram Login** - Безопасная аутентификация через Telegram
- 📊 **AI Analysis** - Профессиональный анализ с использованием GPT
- 📈 **Interactive Charts** - Интерактивные графики с техническими индикаторами
- 💳 **Subscription Management** - Система подписок через Firestore
- ☁️ **Cloud Ready** - Готов к деплою в Google Cloud Run

## Структура проекта

- `backend/` — FastAPI сервер с API и аутентификацией
- `frontend/` — React приложение с Material-UI
- `bot/` — Telegram бот (отдельный сервис)
- `tests/` — Тесты для всех компонентов

## Быстрый старт

### 1. Настройка переменных окружения

Скопируйте `.env.example` в `.env.dev` и заполните необходимые значения:

```bash
cp .env.example .env.dev
```

Обязательные переменные:
- `TELEGRAM_BOT_TOKEN` - токен вашего Telegram бота
- `TELEGRAM_BOT_USERNAME` - username бота (без @)
- `JWT_SECRET_KEY` - секретный ключ для JWT
- `OPENAI_API_KEY` - ключ OpenAI API
- `CRYPTOCOMPARE_API_KEY` - ключ CryptoCompare API

### 2. Локальная разработка

```bash
# Установка зависимостей backend
pip install -r backend/requirements.txt

# Установка зависимостей frontend
cd frontend && npm install && cd ..

# Запуск backend
uvicorn backend.app:app --reload --env-file .env.dev

# Запуск frontend (в отдельном терминале)
cd frontend && npm run dev

# Запуск бота (в отдельном терминале)
cd bot && python bot.py
```

### 3. Docker (рекомендуется)

```bash
# Настройте .env.docker с вашими значениями
cp .env.example .env.docker

# Запуск всех сервисов
docker-compose up --build
```

### 4. Продакшен (Google Cloud Run)

#### 🚀 Быстрое развертывание

**Linux/macOS:**
```bash
# Полная автоматическая настройка
./scripts/setup_complete.sh
```

**Windows:**
```batch
# Пошаговая настройка
scripts\setup_gcp.bat
scripts\deploy_manual.bat
```

#### 📚 Документация
- [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md) - Полное руководство по развертыванию
- [DEPLOYMENT.md](DEPLOYMENT.md) - Техническая документация

#### ☁️ Проект Google Cloud
- **ID проекта**: `chartgenius-444017`
- **Регион**: `us-central1`
- **Сервисы**: Cloud Run, Firestore, Secret Manager

## Тестирование

```bash
# Все тесты
pytest

# Только тесты аутентификации
pytest tests/test_auth.py

# Frontend тесты
cd frontend && npm test
```

## Использование

### Через Telegram бота

1. Найдите вашего бота в Telegram
2. Отправьте команду `/start`
3. Нажмите "Получить анализ"
4. Получите ссылку на полный отчет

### Через веб-интерфейс

1. Откройте веб-приложение
2. Войдите через Telegram Login Widget
3. Получите доступ к полному функционалу

## Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram Bot  │    │   Backend API   │    │   Frontend SPA  │
│                 │    │                 │    │                 │
│ - Webhook       │◄──►│ - FastAPI       │◄──►│ - React         │
│ - Commands      │    │ - JWT Auth      │    │ - Material-UI   │
│ - Inline KB     │    │ - Analysis      │    │ - Redux         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Google Cloud Platform                      │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Cloud Run   │  │ Firestore   │  │ Secret Manager          │ │
│  │ - 3 Services│  │ - Users     │  │ - API Keys              │ │
│  │ - Auto Scale│  │ - Subs      │  │ - Bot Token             │ │
│  │ - HTTPS     │  │ - Analyses  │  │ - JWT Secret            │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Разработка

### Добавление новых индикаторов

1. Обновите `backend/services/data_processor.py`
2. Добавьте визуализацию в `backend/services/viz.py`
3. Обновите frontend компоненты

### Добавление новых команд бота

1. Добавьте обработчик в `bot/bot.py`
2. Зарегистрируйте команду через BotFather
3. Обновите документацию

## Мониторинг

- **Логи**: `gcloud run services logs read SERVICE_NAME`
- **Метрики**: Google Cloud Console > Cloud Run
- **Ошибки**: Cloud Error Reporting
- **Производительность**: Cloud Trace

## Поддержка

Если у вас возникли проблемы:

1. Проверьте [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md) для инструкций по развертыванию
2. Убедитесь, что все переменные окружения настроены правильно
3. Проверьте логи сервисов в Google Cloud Console
4. Создайте issue в репозитории
