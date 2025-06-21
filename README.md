# ChartGenius 🚀

Профессиональная система анализа криптовалютных рынков с использованием ИИ и технических индикаторов.

## 📋 Обзор

ChartGenius - это комплексная система для анализа криптовалютных данных, включающая:
- **Backend API** на FastAPI с интеграцией OpenAI
- **Frontend** на React с интерактивными графиками
- **Telegram Bot** для удобного доступа
- **Продакшн-готовое развертывание** на Google Cloud Platform

## 🏗️ Архитектура

```
ChartGenius/
├── backend/          # FastAPI сервер
├── frontend/         # React приложение
├── bot/             # Telegram бот
├── production/      # Продакшн конфигурация
├── configs/         # Конфигурационные файлы
├── tests/          # Тесты
└── docs/           # Документация
```

## 🚀 Быстрый старт

### Разработка

1. **Клонирование репозитория:**
```bash
git clone <repository-url>
cd chartgenius
```

2. **Настройка переменных окружения:**
```bash
cp .env.example .env.dev
# Отредактируйте .env.dev с вашими API ключами
```

3. **Запуск backend:**
```bash
pip install -r backend/requirements.txt
uvicorn backend.app:app --reload
```

4. **Запуск frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Продакшн развертывание

Для развертывания в Google Cloud Platform:

```bash
cd production
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="europe-west1"

# Настройка секретов
./setup-secrets.sh

# Развертывание
./deploy-production.sh
```

Подробная инструкция: [production/DEPLOYMENT_GUIDE.md](production/DEPLOYMENT_GUIDE.md)

## 🔧 Разработка

### Структура backend
- `routers/` - API endpoints
- `services/` - Бизнес-логика
- `auth/` - Аутентификация и авторизация
- `validators/` - Валидация данных
- `config/` - Конфигурация

### Структура frontend
- `src/components/` - React компоненты
- `src/store/` - Redux store
- `src/services/` - API клиенты

### Тестирование

```bash
# Backend тесты
pytest

# Frontend тесты
cd frontend && npm test

# Все тесты
npm run test:all
```

## 📚 Документация

- [Руководство по развертыванию](production/DEPLOYMENT_GUIDE.md)
- [Настройка секретов](production/SECRETS_SETUP.md)
- [Интеграция с Telegram](docs/telegram_integration.md)
- [Разделение Frontend/Backend](docs/frontend_backend_split.md)

## 🔐 Безопасность

- Все секреты хранятся в Google Cloud Secret Manager
- JWT аутентификация с коротким временем жизни
- CORS настроен для продакшн доменов
- Валидация всех входных данных

## 🛠️ Технологии

**Backend:**
- FastAPI + Python 3.10
- Google Cloud Firestore
- OpenAI API
- CryptoCompare API

**Frontend:**
- React 18 + Vite
- Material-UI v5
- Redux Toolkit
- TradingView Lightweight Charts

**Infrastructure:**
- Google Cloud Run
- Docker
- Google Cloud Secret Manager
- Cloud Logging & Monitoring

## 📊 Возможности

- 📈 Технический анализ с 15+ индикаторами
- 🤖 ИИ-анализ рыночных трендов
- 📱 Telegram интеграция
- 🔄 Реальное время данных
- 👥 Система ролей пользователей
- 📊 Интерактивные графики

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License.

## 📞 Поддержка

При возникновении вопросов:
- Создайте Issue в GitHub
- Проверьте документацию в папке `docs/`
- Обратитесь к администратору
