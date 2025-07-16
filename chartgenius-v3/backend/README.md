# 🚀 ChartGenius v3 Backend

Современный FastAPI backend для технического анализа криптовалют с AI интеграцией.

## 🏗️ Архитектура

```
backend/
├── app.py                    # Основное FastAPI приложение
├── routers/                  # API роутеры
│   ├── analysis.py          # Технический анализ (основной)
│   ├── auth.py              # Аутентификация
│   ├── admin.py             # Административная панель
│   ├── subscription.py      # Подписки и платежи
│   ├── config.py            # Конфигурация
│   └── webhooks.py          # Telegram webhooks
├── services/                 # Бизнес-логика
│   ├── chatgpt_analyzer.py  # AI анализатор
│   ├── crypto_compare_provider.py # CryptoCompare API
│   └── cache_service.py     # Кэширование
├── auth/                     # Аутентификация
│   └── dependencies.py      # JWT и Telegram WebApp auth
├── middleware/               # Middleware компоненты
│   ├── security.py          # Безопасность
│   ├── rate_limiting.py     # Rate limiting
│   └── telegram_webapp.py   # Telegram WebApp
├── config/                   # Конфигурация
│   ├── config.py            # Настройки приложения
│   └── database.py          # Oracle AJD подключение
└── prompt.txt               # AI промпт для анализа
```

## 🔧 Технологии

- **FastAPI 0.115+** - Современный Python web framework
- **Python 3.11+** - Последняя стабильная версия
- **Oracle AJD** - Autonomous JSON Database
- **Redis** - Кэширование и сессии
- **OpenAI o4-mini-2025-04-16** - AI модель для анализа
- **CryptoCompare API** - Источник OHLCV данных
- **Telegram Bot API** - WebApp и платежи
- **JWT** - Аутентификация
- **Docker** - Контейнеризация

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
cd backend
pip install -r requirements.txt
```

### 2. Конфигурация

```bash
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

### 3. Запуск

```bash
# Разработка
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Docker

```bash
# Сборка
docker build -t chartgenius-backend .

# Запуск
docker run -p 8000:8000 --env-file .env chartgenius-backend
```

## 📊 API Endpoints

### Анализ
- `POST /api/analysis/analyze` - Технический анализ символа
- `GET /api/analysis/history` - История анализов
- `GET /api/analysis/history/{id}` - Конкретный анализ

### Аутентификация
- `POST /api/auth/telegram` - Telegram WebApp аутентификация
- `GET /api/auth/profile` - Профиль пользователя
- `POST /api/auth/refresh` - Обновление токена

### Подписки
- `GET /api/subscription/plans` - Планы подписки
- `GET /api/subscription/current` - Текущая подписка
- `POST /api/subscription/purchase` - Покупка подписки

### Администрирование
- `GET /api/admin/stats/users` - Статистика пользователей
- `GET /api/admin/stats/system` - Системная статистика
- `GET /api/admin/users` - Список пользователей

### Webhooks
- `POST /api/webhooks/telegram` - Telegram Bot webhook
- `POST /api/webhooks/telegram-payment` - Telegram Stars payments

## 🔐 Аутентификация

Backend поддерживает два типа аутентификации:

### 1. JWT токены
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/analysis/analyze
```

### 2. Telegram WebApp
```bash
curl -H "X-Telegram-Init-Data: YOUR_INIT_DATA" \
     http://localhost:8000/api/analysis/analyze
```

## 📈 AI Анализ

Система возвращает **24 объекта технического анализа**:

1. `primary_analysis` - Основной анализ тренда
2. `confidence_in_trading_decisions` - Уверенность в решениях
3. `support_resistance_levels` - Уровни поддержки/сопротивления
4. `trend_lines` - Трендовые линии
5. `pivot_points` - Пивот поинты
6. `fibonacci_levels` - Уровни Фибоначчи
7. `volume_analysis` - Анализ объемов
8. `momentum_indicators` - Индикаторы моментума
9. `oscillators` - Осцилляторы
10. `moving_averages` - Скользящие средние
11. `bollinger_bands` - Полосы Боллинджера
12. `ichimoku_cloud` - Облако Ишимоку
13. `candlestick_patterns` - Свечные паттерны
14. `chart_patterns` - Графические паттерны
15. `elliott_wave` - Волны Эллиотта
16. `market_structure` - Рыночная структура
17. `risk_management` - Управление рисками
18. `entry_exit_points` - Точки входа/выхода
19. `price_targets` - Ценовые цели
20. `stop_loss_levels` - Уровни стоп-лосса
21. `market_sentiment` - Рыночные настроения
22. `correlation_analysis` - Корреляционный анализ
23. `volatility_analysis` - Анализ волатильности
24. `time_frame_analysis` - Анализ временных рамок

## 💳 Telegram Stars Payments

Система поддерживает платежи через Telegram Stars:

### Планы подписки:
- **Basic** - 100 ⭐ (20 анализов/день)
- **Premium** - 300 ⭐ (100 анализов/день)
- **Unlimited** - 500 ⭐ (безлимитно)

### Процесс оплаты:
1. Пользователь выбирает план
2. Создается invoice через Telegram Bot API
3. Пользователь оплачивает через Telegram
4. Webhook обрабатывает платеж
5. Подписка активируется автоматически

## 🛡️ Безопасность

### Rate Limiting
- **100 запросов/минуту** для обычных пользователей
- **1000 запросов/час** для API ключей
- Автоматическая блокировка при превышении

### Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (production)

### Валидация
- Telegram WebApp data validation
- JWT token validation
- Input sanitization
- SQL injection protection

## 📊 Мониторинг

### Health Checks
- `GET /health` - Простая проверка
- `GET /api/health` - Детальная проверка

### Логирование
- Структурированные логи
- Ротация логов
- Error tracking

### Метрики
- Request/response times
- Error rates
- Cache hit rates
- Database connections

## 🔧 Конфигурация

### Основные настройки (.env):

```env
# Environment
ENVIRONMENT=production
API_PORT=8000

# AI Model
OPENAI_API_KEY=your-key
OPENAI_MODEL=o4-mini-2025-04-16

# Database
ORACLE_USERNAME=ADMIN
ORACLE_PASSWORD=your-password
ORACLE_DSN=your-dsn

# Telegram
TELEGRAM_BOT_TOKEN=your-token
WEBAPP_URL=https://chartgenius.online

# Cache
REDIS_URL=redis://localhost:6379/0
ENABLE_CACHE=true
```

## 🐳 Docker Deployment

### Single Container
```bash
docker run -d \
  --name chartgenius-backend \
  -p 8000:8000 \
  --env-file .env \
  chartgenius-backend
```

### Docker Compose
```bash
docker-compose up -d
```

## 📝 Разработка

### Структура кода
- Следуем принципам Clean Architecture
- Dependency Injection через FastAPI
- Async/await для всех I/O операций
- Type hints везде

### Тестирование
```bash
pytest tests/
```

### Линтинг
```bash
black .
flake8 .
mypy .
```

## 🔄 CI/CD

### GitHub Actions
- Автоматическое тестирование
- Docker build и push
- Deployment на Oracle Cloud

### Oracle Cloud Deployment
- Оптимизировано под Always Free Tier
- Автоматическое масштабирование
- SSL сертификаты

## 📞 Поддержка

- **Документация**: `/docs` (development)
- **Логи**: `logs/chartgenius.log`
- **Мониторинг**: Prometheus + Grafana
- **Алерты**: Telegram уведомления
