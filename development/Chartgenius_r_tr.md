# 📋 ТЕХНИЧЕСКОЕ ЗАДАНИЕ: АРХИТЕКТУРНЫЕ УЛУЧШЕНИЯ CHARTGENIUS

**Проект:** ChartGenius  
**Версия:** 1.1.0-dev  
**Дата:** 25.06.2025  
**Среда разработки:** development/ (изолированная)  

---

## 🎯 ОБЩИЕ ТРЕБОВАНИЯ

### Принципы разработки:
- ✅ **Стабильность продакшена:** Продакшен-версия 1.0.51 остается нетронутой
- ✅ **Изолированная разработка:** Все изменения только в `development/` директории
- ✅ **Обратная совместимость:** API endpoints должны оставаться совместимыми
- ✅ **Поэтапное внедрение:** Каждый компонент должен работать независимо
- ✅ **Возможность rollback:** Быстрый откат к предыдущей версии

### Технологический стек:
- **Backend:** FastAPI, Python 3.11+, Redis, Celery
- **Frontend:** React 18, Vite, Material-UI
- **Database:** Firestore (существующая), Redis (новая)
- **Storage:** Google Cloud Storage (для промптов)
- **Monitoring:** Prometheus, Grafana
- **Bot:** aiogram (миграция с python-telegram-bot)
- **Market Data:** CCXT (дополнительно к CoinGecko)

---

## 🔧 ЗАДАЧА 1: ADMIN INTERFACE & MONITORING (КРИТИЧЕСКИЙ ПРИОРИТЕТ)

### 1.1 Hybrid Admin Panel

#### Требования:
Создать гибридную админ-панель, состоящую из:
1. **Grafana Dashboard** - технические метрики
2. **Custom Admin Panel** - бизнес-функции

#### Технические детали:

**1.1.1 Prometheus + Grafana Setup**
```yaml
# Файл: development/monitoring/docker-compose.monitoring.yml
# Сервисы: prometheus, grafana, redis, node-exporter
# Порты: 9090 (prometheus), 3002 (grafana), 6379 (redis)
```

**1.1.2 Backend Metrics Integration**
```python
# Файл: development/backend-dev/services/metrics_service.py
# Класс: ChartGeniusMetrics
# Метрики: API requests, LLM usage, user actions, errors, cache hits/misses
```

**1.1.3 Enhanced Admin Router**
```python
# Файл: development/backend-dev/routers/admin_enhanced.py
# Endpoints:
# GET /admin/enhanced/health - системное здоровье
# POST /admin/enhanced/service/restart - перезапуск сервисов
# POST /admin/enhanced/llm/config - конфигурация LLM
# POST /admin/enhanced/llm/prompt - управление промптами
# POST /admin/enhanced/user/manage - управление пользователями
# GET /admin/enhanced/metrics/prometheus - метрики Prometheus
```

#### 1.1.4 Система управления промптами

**Структура хранения промптов:**

**Cloud Storage структура:**
```
gs://chartgenius-prompts/
├── technical_analysis/
│   ├── v1.0.txt
│   ├── v1.1.txt
│   └── active.txt (symlink на активную версию)
├── fundamental_analysis/
│   ├── v1.0.txt
│   └── active.txt
├── sentiment_analysis/
│   ├── v1.0.txt
│   └── active.txt
└── risk_assessment/
    ├── v1.0.txt
    └── active.txt
```

**Метаданные промптов в Firestore:**
```javascript
// Коллекция: prompt_metadata
// Документы: technical_analysis, fundamental_analysis, sentiment_analysis, risk_assessment
{
  "active_version": "1.1",
  "versions": {
    "1.0": {
      "created_at": timestamp,
      "created_by": "admin",
      "description": "Базовый промпт для технического анализа",
      "file_path": "gs://chartgenius-prompts/technical_analysis/v1.0.txt",
      "file_size": 2048,
      "parameters": {
        "temperature": 0.7,
        "max_tokens": 4000
      }
    },
    "1.1": {
      "created_at": timestamp,
      "created_by": "admin",
      "description": "Улучшенный промпт с дополнительными инструкциями",
      "file_path": "gs://chartgenius-prompts/technical_analysis/v1.1.txt",
      "file_size": 3072,
      "parameters": {
        "temperature": 0.7,
        "max_tokens": 4000
      }
    }
  },
  "updated_at": timestamp,
  "updated_by": "admin"
}
```

**Cloud Storage Service:**
```python
# Файл: development/backend-dev/services/cloud_storage_service.py
# Класс: CloudStorageService
# Методы:
# - upload_prompt(prompt_type: str, version: str, content: str)
# - download_prompt(prompt_type: str, version: str) -> str
# - get_active_prompt(prompt_type: str) -> str
# - list_prompt_versions(prompt_type: str) -> List[str]
# - set_active_version(prompt_type: str, version: str)
```

**API для управления промптами:**
```python
# POST /admin/enhanced/llm/prompt/upload
{
  "prompt_type": "technical_analysis",
  "prompt_content": "Очень длинный промпт с множеством инструкций...",
  "version": "1.1",
  "description": "Обновленный промпт для технического анализа",
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 4000
  }
}

# GET /admin/enhanced/llm/prompts - список всех промптов с метаданными
# GET /admin/enhanced/llm/prompts/{type} - метаданные конкретного промпта
# GET /admin/enhanced/llm/prompts/{type}/content - содержимое активного промпта
# GET /admin/enhanced/llm/prompts/{type}/versions/{version} - содержимое версии
# PUT /admin/enhanced/llm/prompts/{type}/activate/{version} - активация версии
# DELETE /admin/enhanced/llm/prompts/{type}/versions/{version} - удаление версии
```

**Интеграция с LLM Service:**
```python
# Модификация: development/backend-dev/services/llm_service.py
# Добавить зависимость: CloudStorageService
# Добавить метод: get_active_prompt(prompt_type: str) -> str
# Кэширование промптов в Redis на 1 час
# Использование промптов из Cloud Storage вместо hardcoded
```

#### 1.1.5 Grafana Dashboards

**Создать дашборды:**
1. **System Overview** - общее состояние системы
2. **API Performance** - производительность API
3. **LLM Usage** - использование LLM провайдеров
4. **User Activity** - активность пользователей
5. **Error Monitoring** - отслеживание ошибок

**Файлы конфигурации:**
```
development/monitoring/grafana/dashboards/
├── system-overview.json
├── api-performance.json
├── llm-usage.json
├── user-activity.json
└── error-monitoring.json
```

### 1.2 Критические метрики для мониторинга

**Операционные метрики:**
- LLM requests/hour с порогом >100
- API latency с порогом >2s
- Error rate с порогом >5%
- Active users count
- Daily LLM spend с порогом >$50

**Бизнес метрики:**
- Daily active users
- Analysis requests count
- Subscription revenue
- User retention rate
- Feature usage statistics

---

## ⚡ ЗАДАЧА 2: EVENT-DRIVEN ARCHITECTURE

### 2.1 Background Tasks с Celery

#### Требования:
Внедрить асинхронную обработку long-running операций (>30 сек) с использованием Celery + Redis.

#### Технические детали:

**2.1.1 Task Service**
```python
# Файл: development/backend-dev/services/task_service.py
# Celery app с Redis broker
# Задачи: process_analysis_task, cleanup_old_tasks
# Класс: TaskManager для управления задачами
```

**2.1.2 Celery Configuration**
```python
# Настройки:
# broker: redis://localhost:6379/0
# backend: redis://localhost:6379/0
# task_time_limit: 300 секунд
# task_soft_time_limit: 240 секунд
# worker_prefetch_multiplier: 1
```

**2.1.3 Task Status Tracking**
```python
# Статусы: PENDING, STARTED, PROCESSING, SUCCESS, FAILURE, RETRY
# Хранение в Redis с TTL 24 часа
# Ключи: task_info:{task_id}, analysis_result:{task_id}
```

**2.1.4 API Endpoints для задач**
```python
# POST /api/analysis/async - запуск асинхронного анализа
# GET /api/analysis/status/{task_id} - статус задачи
# DELETE /api/analysis/cancel/{task_id} - отмена задачи
# GET /api/analysis/result/{task_id} - результат задачи
```

### 2.2 WebSocket для Real-time уведомлений

#### Требования:
Реализовать WebSocket соединения для уведомлений о статусе задач в реальном времени.

#### Технические детали:

**2.2.1 WebSocket Service**
```python
# Файл: development/backend-dev/services/websocket_service.py
# Класс: ConnectionManager
# Функции: connect, disconnect, send_personal_message, broadcast_message
# Redis pub/sub для масштабирования
```

**2.2.2 WebSocket Endpoint**
```python
# Endpoint: /ws/{user_id}
# Аутентификация через JWT token в query params
# Поддержка подписки на задачи: subscribe_task, ping/pong
```

**2.2.3 Notification Types**
```javascript
// Типы уведомлений:
{
  "type": "analysis_started",
  "task_id": "uuid",
  "symbol": "BTCUSDT",
  "message": "Анализ запущен"
}

{
  "type": "task_update", 
  "task_id": "uuid",
  "data": {
    "progress": 60,
    "status": "Генерация AI анализа..."
  }
}

{
  "type": "analysis_completed",
  "task_id": "uuid",
  "action": {
    "type": "view_result",
    "url": "/analysis/result/{task_id}"
  }
}
```

**2.2.4 Frontend Integration**
```javascript
// Файл: development/frontend-dev/src/services/websocket.js
// Подключение к WebSocket
// Обработка уведомлений
// Автоматическое переподключение
```

---

## 🤖 ЗАДАЧА 3: TELEGRAM BOT MIGRATION

### 3.1 Миграция на aiogram

#### Требования:
Поэтапная миграция с python-telegram-bot на aiogram с сохранением всех функций.

#### Технические детали:

**3.1.1 Новая структура бота**
```python
# Файл: development/bot-dev/bot_aiogram.py
# Использование aiogram 3.x
# Router-based архитектура
# Middleware для auth и logging
```

**3.1.2 Command Handlers Migration**
```python
# Команды для миграции:
# /start - главное меню с WebApp
# /help - справка
# /settings - настройки пользователя
# /watch - добавить в отслеживание (если есть)
# /unwatch - убрать из отслеживания (если есть)
```

**3.1.3 Callback Query Handlers**
```python
# Обработчики:
# quick_analysis - быстрый анализ
# analyze_{symbol} - анализ конкретного символа
# settings_* - настройки
# back_to_menu - возврат в меню
```

**3.1.4 WebApp Integration**
```python
# WebAppInfo вместо WebApp
# Сохранение URL и функциональности
# Тестирование auth flow
```

**3.1.5 Middleware Migration**
```python
# AuthMiddleware - проверка пользователей через backend
# LoggingMiddleware - логирование событий
# Сохранение функциональности rate limiting
```

### 3.2 Deployment Strategy

**3.2.1 Parallel Deployment**
```yaml
# development/docker-compose.dev.yml
# Добавить сервис bot-aiogram на порт 8003
# Параллельная работа с существующим ботом
```

**3.2.2 Testing Environment**
```python
# Отдельный тестовый бот для aiogram версии
# Тестирование всех user flows
# Сравнение производительности
```

---

## 📊 ЗАДАЧА 4: CCXT INTEGRATION

### 4.1 Поэтапная интеграция CCXT

#### Требования:
Добавить CCXT как дополнительный источник данных с fallback логикой.

#### Технические детали:

**4.1.1 CCXT Service**
```python
# Файл: development/backend-dev/services/ccxt_service.py
# Класс: CCXTService
# Поддерживаемые биржи: binance, coinbase, kraken, bybit
# Fallback order по приоритету
```

**4.1.2 Exchange Configuration**
```python
# ExchangeConfig dataclass:
# name, priority, rate_limit, timeout, retry_attempts
# ExchangeStatus enum: HEALTHY, DEGRADED, UNAVAILABLE
# Автоматическое health monitoring
```

**4.1.3 Data Fetching Methods**
```python
# get_ohlcv_data() - OHLCV данные с fallback
# get_ticker_data() - текущие цены
# health_check_all() - проверка всех бирж
# get_supported_symbols() - поддерживаемые символы
```

**4.1.4 Integration with Market Data Service**
```python
# Модификация: development/backend-dev/services/market_data_service.py
# Добавить CCXT как fallback для CoinGecko
# Приоритет: CoinGecko -> CCXT (binance) -> CCXT (coinbase) -> CCXT (kraken)
```

### 4.2 API Endpoints

**4.2.1 New Endpoints**
```python
# GET /api/market/exchanges - список бирж и их статус
# GET /api/market/symbols/{exchange} - символы конкретной биржи
# GET /api/market/ticker/{symbol} - текущая цена
# GET /api/market/health - здоровье всех источников данных
```

**4.2.2 Enhanced Existing Endpoints**
```python
# GET /api/market/ohlcv - добавить параметр source=ccxt
# Автоматический fallback при недоступности CoinGecko
```

---

## 🎨 ЗАДАЧА 5: ADMIN PANEL FRONTEND

### 5.1 Комплексная админ-панель

#### Требования:
Создать полнофункциональную админ-панель, объединяющую мониторинг системы и управление всеми компонентами.

#### Технические детали:

**5.1.1 Admin Dashboard (Главная страница)**
```javascript
// Файл: development/frontend-dev/src/pages/AdminDashboard.jsx
// Компоненты:
// - SystemOverview - общее состояние системы
// - QuickActions - быстрые действия
// - RecentActivity - последняя активность
// - AlertsPanel - критические уведомления
// - MetricsCards - ключевые метрики (API calls, users, errors)
```

**5.1.2 System Health Monitor**
```javascript
// Файл: development/frontend-dev/src/components/admin/SystemHealth.jsx
// Функции:
// - Real-time статус всех сервисов
// - Метрики производительности (CPU, Memory, Response Time)
// - Статус внешних зависимостей (Redis, Firestore, CCXT exchanges)
// - Графики производительности (интеграция с Grafana)
// - Алерты и уведомления
// - Кнопки перезапуска сервисов
```

**5.1.3 User Management Interface**
```javascript
// Файл: development/frontend-dev/src/components/admin/UserManager.jsx
// Функции:
// - Список всех пользователей с фильтрацией
// - Управление ролями (user, premium, vip, admin)
// - Блокировка/разблокировка пользователей
// - Статистика использования по пользователям
// - Сброс лимитов API
// - История действий пользователей
```

**5.1.4 Prompt Management Interface**
```javascript
// Файл: development/frontend-dev/src/components/admin/PromptManager.jsx
// Функции:
// - Список всех типов промптов (technical_analysis, fundamental_analysis, etc.)
// - Просмотр активных версий промптов
// - Загрузка новых версий промптов (file upload)
// - Редактор промптов с syntax highlighting
// - Предварительный просмотр промптов
// - Версионирование и история изменений
// - Активация/деактивация версий
// - Параметры промптов (temperature, max_tokens)
// - Тестирование промптов на тестовых данных
```

**5.1.5 LLM Configuration Panel**
```javascript
// Файл: development/frontend-dev/src/components/admin/LLMConfig.jsx
// Функции:
// - Конфигурация LLM провайдеров
// - Переключение между моделями
// - Настройка параметров (temperature, max_tokens, timeout)
// - Мониторинг использования и costs
// - Статистика по провайдерам
// - Health check провайдеров
```

**5.1.6 Task Management Interface**
```javascript
// Файл: development/frontend-dev/src/components/admin/TaskManager.jsx
// Функции:
// - Список активных задач
// - Мониторинг очереди Celery
// - Отмена задач
// - Статистика выполнения задач
// - Логи задач
// - Performance метрики
```

**5.1.7 WebSocket Integration**
```javascript
// Файл: development/frontend-dev/src/services/adminWebSocket.js
// Функции:
// - Real-time обновления метрик
// - Уведомления о системных событиях
// - Live логи
// - Автоматическое обновление статусов
```

### 5.2 Real-time Updates для основного приложения

#### Требования:
Интеграция WebSocket для real-time уведомлений пользователей.

#### Технические детали:

**5.2.1 WebSocket Client**
```javascript
// Файл: development/frontend-dev/src/services/websocketService.js
// Подключение к WebSocket endpoint
// Автоматическое переподключение
// Обработка различных типов сообщений
```

**5.2.2 Task Status Component**
```javascript
// Файл: development/frontend-dev/src/components/TaskStatus.jsx
// Отображение прогресса задач
// Real-time обновления через WebSocket
// Кнопки отмены задач
```

**5.2.3 Notification System**
```javascript
// Файл: development/frontend-dev/src/components/NotificationCenter.jsx
// Toast уведомления
// Звуковые уведомления (опционально)
// История уведомлений
```

---

## 🔧 ЗАДАЧА 6: INFRASTRUCTURE IMPROVEMENTS

### 6.1 Docker Configuration

#### Требования:
Обновить Docker конфигурацию для новых сервисов.

#### Технические детали:

**6.1.1 Updated docker-compose.dev.yml**
```yaml
# Добавить сервисы:
# redis - для Celery и кэширования
# celery-worker - обработка задач
# celery-beat - планировщик задач (если нужен)
# prometheus - метрики
# grafana - мониторинг
```

**6.1.2 Environment Variables**
```bash
# development/.env.development
# Добавить переменные для:
# REDIS_URL, CELERY_BROKER_URL, CELERY_RESULT_BACKEND
# PROMETHEUS_URL, GRAFANA_URL
# CCXT_EXCHANGES, WEBHOOK_SECRET
# GOOGLE_CLOUD_STORAGE_BUCKET=chartgenius-prompts
# GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

### 6.2 Health Checks

#### Требования:
Добавить health checks для всех сервисов.

#### Технические детали:

**6.2.1 Service Health Endpoints**
```python
# /health - базовый health check
# /health/detailed - детальная информация
# /health/dependencies - статус зависимостей
```

**6.2.2 Docker Health Checks**
```dockerfile
# Добавить HEALTHCHECK инструкции в Dockerfile
# Проверка доступности сервисов
```

---

## 📝 ЗАДАЧА 7: TESTING & DOCUMENTATION

### 7.1 Testing Requirements

#### Требования:
Создать тесты для всех новых компонентов.

#### Технические детали:

**7.1.1 Backend Tests**
```python
# development/backend-dev/tests/
# test_task_service.py - тесты Celery задач
# test_websocket_service.py - тесты WebSocket
# test_ccxt_service.py - тесты CCXT интеграции
# test_admin_enhanced.py - тесты админ API
```

**7.1.2 Frontend Tests**
```javascript
# development/frontend-dev/src/tests/
# WebSocketService.test.js
# TaskStatus.test.jsx
# AdminDashboard.test.jsx
```

**7.1.3 Integration Tests**
```python
# Тесты взаимодействия компонентов
# End-to-end тесты критических путей
```

### 7.2 Documentation

#### Требования:
Обновить документацию для новых функций.

#### Технические детали:

**7.2.1 API Documentation**
```python
# Обновить FastAPI автодокументацию
# Добавить примеры запросов/ответов
# Документировать WebSocket API
```

**7.2.2 Deployment Guide**
```markdown
# development/docs/deployment.md
# Инструкции по развертыванию
# Конфигурация мониторинга
# Troubleshooting guide
```

---

## 🚀 ПОРЯДОК ВЫПОЛНЕНИЯ

### Неделя 1-2: Admin Interface Backend (Критический приоритет)
1. Настройка Prometheus + Grafana
2. Создание metrics service
3. Разработка enhanced admin router
4. Cloud Storage service для промптов
5. Система управления промптами (backend)

### Неделя 3-4: Event-Driven Architecture
1. Настройка Redis + Celery
2. Создание task service
3. WebSocket service
4. Backend интеграция
5. Тестирование асинхронных операций

### Неделя 5-6: Admin Panel Frontend
1. Admin Dashboard (главная страница)
2. System Health Monitor
3. User Management Interface
4. Prompt Management Interface (с Cloud Storage)
5. LLM Configuration Panel
6. Task Management Interface

### Неделя 7-8: Telegram Bot Migration
1. Создание aiogram версии
2. Миграция handlers
3. Тестирование функциональности
4. Параллельное развертывание
5. Переключение на новую версию

### Неделя 9-10: CCXT Integration
1. Создание CCXT service
2. Интеграция с market data service
3. Fallback логика
4. Health monitoring
5. API endpoints

### Неделя 11-12: Testing & Documentation
1. Unit тесты
2. Integration тесты
3. Frontend real-time updates
4. Документация API
5. Performance тестирование

---

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

### Безопасность:
- Все admin endpoints требуют аутентификации
- Валидация всех входных данных
- Rate limiting для API endpoints
- Безопасное хранение секретов в переменных окружения

### Производительность:
- Кэширование результатов в Redis
- Асинхронная обработка тяжелых операций
- Connection pooling для внешних API
- Мониторинг производительности

### Совместимость:
- Обратная совместимость API
- Graceful degradation при недоступности сервисов
- Fallback механизмы для всех внешних зависимостей

### Мониторинг:
- Логирование всех критических операций
- Метрики для всех сервисов
- Алерты для критических ошибок
- Health checks для всех компонентов

---

## 📋 ЧЕКЛИСТ ГОТОВНОСТИ

### Перед началом разработки:
- [ ] Убедиться что продакшен-версия 1.0.51 стабильна
- [ ] Создать backup текущей development/ директории
- [ ] Настроить мониторинг development-окружения
- [ ] Подготовить тестовые данные и аккаунты
- [ ] Проверить доступность всех внешних сервисов

### Критерии приемки:
- [ ] Все новые API endpoints работают корректно
- [ ] WebSocket соединения стабильны
- [ ] Админ-панель функциональна
- [ ] Telegram bot полностью мигрирован
- [ ] CCXT интеграция работает с fallback
- [ ] Все тесты проходят успешно
- [ ] Документация обновлена
- [ ] Performance не деградировал

### Критерии готовности к продакшену:
- [ ] Load testing пройден успешно
- [ ] Security audit выполнен
- [ ] Monitoring и alerting настроены
- [ ] Rollback процедуры протестированы
- [ ] Team training завершен

---

## 🔗 СВЯЗАННЫЕ ДОКУМЕНТЫ

- `development/README-DEV.md` - Инструкции по разработке
- `development/monitoring/README.md` - Настройка мониторинга
- `development/bot-dev/migration_plan.md` - План миграции бота
- `development/docs/api.md` - Документация API
- `development/tests/README.md` - Инструкции по тестированию

---

## 📞 КОНТАКТЫ И ПОДДЕРЖКА

### Техническая поддержка:
- **Primary:** Development Team Lead
- **Backend:** Backend Developer
- **Frontend:** Frontend Developer
- **DevOps:** Infrastructure Engineer

### Каналы связи:
- **Slack:** #chartgenius-dev
- **Email:** dev-team@chartgenius.com
- **Issues:** GitHub Issues в репозитории

### Экстренные ситуации:
- **Критические баги:** Немедленно в Slack + email
- **Проблемы продакшена:** Hotline + escalation
- **Вопросы по ТЗ:** Development Team Lead

---

**Статус:** Готово к разработке
**Среда:** development/ (изолированная)
**Версия:** 1.1.0-dev
**Дата создания:** 25.06.2025
**Автор:** Technical Architect
**Утверждено:** Project Manager
