# 🚀 ChartGenius Development Environment
**Версия: 1.1.0-dev**  
**Дата: 2025-06-26**

## 📋 Обзор

Изолированная среда разработки ChartGenius с полным набором архитектурных улучшений:

- ✅ **Event-driven архитектура** (Celery + WebSocket)
- ✅ **Admin Interface Backend** (Cloud Storage + Metrics)
- ✅ **Admin Panel Frontend** (React компоненты)
- ✅ **Telegram Bot Migration** (aiogram)
- ✅ **CCXT Integration** (Multi-exchange support)
- ✅ **Enhanced Monitoring** (Prometheus + Grafana)

## 🏗️ Архитектура

```
development/
├── backend-dev/          # FastAPI backend с новыми сервисами
├── frontend-dev/         # React frontend с админ-панелью
├── bot-dev/             # Telegram bot на aiogram
├── monitoring/          # Prometheus + Grafana + Redis
├── docs/               # Документация
└── docker-compose.dev.yml
```

## 🚀 Быстрый старт

### 1. Предварительные требования
```bash
# Установленные инструменты
- Docker & Docker Compose
- Node.js 18+ (для локальной разработки)
- Python 3.11+ (для локальной разработки)
- Git
```

### 2. Клонирование и настройка
```bash
# Клонирование репозитория
git clone https://github.com/2511319/GeniusO4_full.git
cd GeniusO4_full/development

# Копирование конфигурации
cp .env.development.example .env.development
# Отредактируйте .env.development с вашими API ключами

# Добавление service account для Google Cloud
# Поместите service-account.json в корень development/
```

### 3. Запуск всех сервисов
```bash
# Запуск полной среды разработки
docker-compose -f docker-compose.dev.yml up -d

# Проверка статуса
docker-compose -f docker-compose.dev.yml ps
```

### 4. Доступ к сервисам
```
Frontend:     http://localhost:3001
Backend API:  http://localhost:8001
Bot Webhook:  http://localhost:8002
Redis:        localhost:6380
Swagger UI:   http://localhost:8001/docs
Admin Panel:  http://localhost:3001/admin
```

## 🔧 Конфигурация

### Environment Variables
```bash
# Основные настройки
ENVIRONMENT=development
DEBUG=true
VERSION=1.1.0-dev

# API ключи (обязательно настроить)
OPENAI_API_KEY=your_openai_api_key
CRYPTOCOMPARE_API_KEY=your_cryptocompare_api_key
TELEGRAM_BOT_TOKEN=7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0

# Google Cloud
GOOGLE_CLOUD_STORAGE_BUCKET=chartgenius-prompts-dev
GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json

# Feature flags
FEATURE_ASYNC_ANALYSIS=true
FEATURE_WEBSOCKET_NOTIFICATIONS=true
FEATURE_CCXT_INTEGRATION=true
FEATURE_ADMIN_PANEL=true
```

## 🛠️ Разработка

### Backend Development
```bash
# Локальная разработка backend
cd backend-dev
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Запуск в dev режиме
uvicorn app:app --reload --host 0.0.0.0 --port 8001

# Запуск Celery worker
celery -A backend.services.task_service worker --loglevel=info

# Тесты
pytest tests/ -v
```

### Frontend Development
```bash
# Локальная разработка frontend
cd frontend-dev
npm install

# Запуск в dev режиме
npm run dev

# Тесты
npm test

# Сборка
npm run build
```

### Bot Development
```bash
# Локальная разработка бота
cd bot-dev
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Запуск бота
python bot_aiogram.py
```

## 📊 Мониторинг

### Prometheus Metrics
```bash
# Запуск мониторинга
docker-compose -f monitoring/docker-compose.monitoring.yml up -d

# Доступ к сервисам
Prometheus: http://localhost:9090
Grafana:    http://localhost:3000 (admin/admin)
Redis UI:   http://localhost:8081
```

### Доступные метрики
```
# API метрики
chartgenius_api_requests_total
chartgenius_api_request_duration_seconds

# LLM метрики
chartgenius_llm_requests_total
chartgenius_llm_tokens_used_total
chartgenius_llm_cost_usd_total

# Системные метрики
chartgenius_active_users
chartgenius_cache_hits_total
chartgenius_errors_total

# Бизнес метрики
chartgenius_analyses_total
chartgenius_daily_revenue_usd
```

## 🔌 API Endpoints

### Новые Admin Endpoints
```
POST   /api/llm/prompt/upload          # Загрузка промпта
GET    /api/llm/prompts                # Список промптов
GET    /api/llm/prompts/{type}         # Метаданные промпта
PUT    /api/llm/prompts/{type}/activate/{version}  # Активация версии
DELETE /api/llm/prompts/{type}/versions/{version}  # Удаление версии

GET    /api/market/exchanges           # Статус бирж
GET    /api/market/symbols/{exchange}  # Символы биржи
GET    /api/market/ticker/{symbol}     # Тикер символа
GET    /api/market/health              # Общее состояние
```

### Async Analysis Endpoints
```
POST   /api/analyze/async              # Запуск асинхронного анализа
GET    /api/analyze/status/{task_id}   # Статус задачи
GET    /api/analyze/result/{task_id}   # Результат анализа
DELETE /api/analyze/cancel/{task_id}   # Отмена задачи
```

### WebSocket
```
WS     /ws/{user_id}                   # Real-time уведомления
```

## 🧪 Тестирование

### Backend Tests
```bash
# Все тесты
pytest tests/ -v

# Конкретные тесты
pytest tests/test_cloud_storage_service.py -v
pytest tests/test_ccxt_service.py -v
pytest tests/test_websocket_service.py -v

# Интеграционные тесты
pytest tests/ -m integration

# Покрытие кода
pytest --cov=backend tests/
```

### Frontend Tests
```bash
# Unit тесты
npm test

# E2E тесты
npm run test:e2e

# Линтинг
npm run lint
```

## 🐛 Отладка

### Логи
```bash
# Логи всех сервисов
docker-compose -f docker-compose.dev.yml logs -f

# Логи конкретного сервиса
docker-compose -f docker-compose.dev.yml logs -f backend-dev
docker-compose -f docker-compose.dev.yml logs -f celery-worker-dev

# Логи в файлах
tail -f logs/chartgenius-dev.log
```

### Debugging Tools
```bash
# Redis CLI
docker exec -it chartgenius-redis-dev redis-cli

# Backend shell
docker exec -it chartgenius-backend-dev bash

# Database inspection
# Firestore через Google Cloud Console
```

## 🔄 Workflow

### Git Workflow
```bash
# Работа в development ветке
git checkout development
git pull origin development

# Создание feature ветки
git checkout -b feature/new-feature
# ... разработка ...
git commit -m "feat: добавлена новая функция"
git push origin feature/new-feature

# Создание PR в development
```

### Deployment Workflow
```bash
# Локальное тестирование
docker-compose -f docker-compose.dev.yml up --build

# Проверка health checks
curl http://localhost:8001/health
curl http://localhost:8001/metrics

# Тестирование API
curl http://localhost:8001/docs
```

## 📚 Документация

### Доступная документация
```
docs/ARCHITECTURE.md     # Архитектура системы
docs/API.md             # API документация
docs/DEPLOYMENT.md      # Инструкции по деплою
docs/TESTING.md         # Руководство по тестированию
```

### Swagger/OpenAPI
```
http://localhost:8001/docs     # Swagger UI
http://localhost:8001/redoc    # ReDoc
```

## 🚨 Troubleshooting

### Частые проблемы

#### 1. Порты заняты
```bash
# Проверка занятых портов
netstat -tulpn | grep :3001
netstat -tulpn | grep :8001

# Остановка конфликтующих сервисов
docker-compose -f docker-compose.dev.yml down
```

#### 2. Проблемы с Redis
```bash
# Перезапуск Redis
docker-compose -f docker-compose.dev.yml restart redis-dev

# Очистка Redis
docker exec -it chartgenius-redis-dev redis-cli FLUSHALL
```

#### 3. Проблемы с Google Cloud
```bash
# Проверка service account
cat service-account.json | jq .

# Проверка переменных окружения
docker exec -it chartgenius-backend-dev env | grep GOOGLE
```

#### 4. WebSocket проблемы
```bash
# Проверка WebSocket соединения
wscat -c ws://localhost:8001/ws/test_user

# Логи WebSocket
docker-compose logs -f backend-dev | grep websocket
```

## 🎯 Следующие шаги

### Планируемые улучшения
- [ ] GraphQL API layer
- [ ] Advanced caching strategies
- [ ] Machine Learning integration
- [ ] Mobile app development
- [ ] Multi-language support

### Оптимизации
- [ ] Performance monitoring
- [ ] Advanced error tracking
- [ ] Automated testing pipeline
- [ ] Security enhancements

---

**Документация обновлена:** 2025-06-26  
**Версия:** 1.1.0-dev  
**Статус:** Готово к разработке ✅

## 🤝 Поддержка

Для вопросов и поддержки:
- GitHub Issues: [Создать issue](https://github.com/2511319/GeniusO4_full/issues)
- Документация: `development/docs/`
- Логи: `development/logs/`
