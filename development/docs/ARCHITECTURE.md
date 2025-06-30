# 🏗️ ChartGenius Architecture Documentation
**Версия: 1.1.0-dev**  
**Дата: 2025-06-26**

## 📋 Обзор

ChartGenius - это система анализа криптовалют с микросервисной архитектурой, включающая:

- **Backend API** (FastAPI + Python)
- **Frontend Web App** (React + Material-UI)
- **Telegram Bot** (aiogram)
- **Admin Panel** (React компоненты)
- **Real-time WebSocket** (для уведомлений)
- **Background Tasks** (Celery + Redis)
- **Market Data Integration** (CCXT + CoinGecko)
- **Monitoring** (Prometheus + Grafana)

## 🎯 Архитектурные принципы

### 1. Event-Driven Architecture
- Асинхронная обработка задач через Celery
- Real-time уведомления через WebSocket
- Pub/Sub паттерн для межсервисного взаимодействия

### 2. Microservices Pattern
- Изолированные сервисы с четкими границами
- API Gateway для маршрутизации запросов
- Независимое масштабирование компонентов

### 3. Cloud-Native Design
- Контейнеризация с Docker
- Stateless сервисы
- Внешние хранилища состояния (Redis, Firestore)

### 4. Resilience & Reliability
- Circuit Breaker паттерн для внешних API
- Retry механизмы с exponential backoff
- Health checks и мониторинг

## 🔧 Компоненты системы

### Backend Services

#### 1. API Gateway (FastAPI)
```
development/backend-dev/app.py
├── Роутеры:
│   ├── /api/analysis - Анализ криптовалют
│   ├── /api/admin - Базовое администрирование
│   ├── /api/admin-enhanced - Расширенная админ-панель
│   ├── /api/mod - Модерация
│   └── /api/watch - Watchlist
├── WebSocket endpoint: /ws/{user_id}
└── Metrics endpoint: /metrics
```

#### 2. Core Services
```
development/backend-dev/services/
├── cloud_storage_service.py - Управление промптами в Cloud Storage
├── ccxt_service.py - Интеграция с криптобиржами
├── market_data_service.py - Унифицированный доступ к рыночным данным
├── websocket_service.py - Real-time уведомления
├── task_service.py - Фоновые задачи (Celery)
├── metrics_service.py - Сбор метрик (Prometheus)
└── llm_service.py - Интеграция с LLM провайдерами
```

#### 3. Data Providers
```
development/backend-dev/services/providers/
├── openai_provider.py - OpenAI GPT интеграция
├── google_provider.py - Google Vertex AI
├── huggingface_provider.py - HuggingFace модели
└── base.py - Базовый интерфейс провайдеров
```

### Frontend Components

#### 1. Main Application
```
development/frontend-dev/src/
├── App.jsx - Главное приложение
├── pages/
│   ├── Home.jsx - Главная страница
│   ├── Login.jsx - Авторизация
│   ├── UserDashboard.jsx - Пользовательская панель
│   └── AdminDashboard.jsx - Админ-панель
└── components/
    └── admin/ - Компоненты админ-панели
```

#### 2. Admin Panel Components
```
development/frontend-dev/src/components/admin/
├── SystemHealth.jsx - Мониторинг системы
├── UserManager.jsx - Управление пользователями
├── PromptManager.jsx - Управление промптами
├── MarketDataManager.jsx - Управление источниками данных
└── TaskMonitor.jsx - Мониторинг задач
```

#### 3. Services
```
development/frontend-dev/src/services/
└── websocketService.js - WebSocket клиент
```

### Bot Service

#### 1. Telegram Bot (aiogram)
```
development/bot-dev/
├── bot_aiogram.py - Основной бот на aiogram
├── handlers/ - Обработчики команд и сообщений
└── middleware/ - Промежуточное ПО
```

### Infrastructure

#### 1. Containerization
```
development/
├── docker-compose.dev.yml - Среда разработки
├── backend-dev/Dockerfile
├── frontend-dev/Dockerfile
└── bot-dev/Dockerfile
```

#### 2. Monitoring
```
development/monitoring/
├── docker-compose.monitoring.yml
├── prometheus/prometheus.yml
├── grafana/dashboards/
└── redis/ - Конфигурация Redis
```

## 🔄 Data Flow

### 1. Analysis Request Flow
```
User Request → API Gateway → Task Queue (Celery) → Background Worker
     ↓
WebSocket Notification ← Real-time Updates ← Analysis Engine
     ↓
Result Storage (Redis) → API Response → Frontend Update
```

### 2. Market Data Flow
```
External APIs (CCXT/CoinGecko) → Market Data Service → Cache (Redis)
     ↓
Fallback Chain: CoinGecko → Binance → Coinbase → Kraken → Bybit
     ↓
Normalized Data → Analysis Engine → LLM Processing
```

### 3. Admin Operations Flow
```
Admin Panel → API Gateway → Cloud Storage Service → Google Cloud Storage
     ↓
Prompt Management → LLM Service → Analysis Engine
     ↓
Metrics Collection → Prometheus → Grafana Dashboard
```

## 🔐 Security Architecture

### 1. Authentication & Authorization
- JWT токены для API аутентификации
- Telegram WebApp аутентификация
- Role-based access control (user/premium/vip/admin)

### 2. Data Protection
- HTTPS/WSS для всех соединений
- API rate limiting
- Input validation и sanitization
- CORS политики

### 3. Secrets Management
- Google Cloud Secret Manager для продакшена
- Environment variables для разработки
- Encrypted storage для sensitive data

## 📊 Monitoring & Observability

### 1. Metrics Collection
```
Application Metrics (Prometheus):
├── API request metrics (duration, status codes)
├── LLM usage metrics (tokens, cost, latency)
├── User activity metrics
├── System health metrics
└── Business metrics (analyses performed)
```

### 2. Logging
```
Structured Logging:
├── Application logs (JSON format)
├── Access logs (nginx format)
├── Error tracking
└── Audit logs
```

### 3. Health Checks
```
Health Check Endpoints:
├── /health - Basic health check
├── /metrics - Prometheus metrics
├── /api/market/health - Market data sources health
└── WebSocket connection monitoring
```

## 🚀 Deployment Architecture

### 1. Development Environment
```
Local Development:
├── Docker Compose для всех сервисов
├── Hot reload для frontend/backend
├── Local Redis и Prometheus
└── Mock external services
```

### 2. Production Environment (Google Cloud)
```
Google Cloud Platform:
├── Cloud Run для API сервисов
├── Cloud Storage для промптов и файлов
├── Firestore для основных данных
├── Cloud Secret Manager для секретов
├── Cloud Monitoring для метрик
└── Cloud Load Balancer
```

## 🔧 Configuration Management

### 1. Environment Variables
```
Configuration Layers:
├── .env.development - Разработка
├── .env.production - Продакшен
├── Docker environment - Контейнеры
└── Cloud environment - Google Cloud
```

### 2. Feature Flags
```
Feature Management:
├── FEATURE_ASYNC_ANALYSIS
├── FEATURE_WEBSOCKET_NOTIFICATIONS
├── FEATURE_CCXT_INTEGRATION
├── FEATURE_ADMIN_PANEL
└── FEATURE_PROMPT_MANAGEMENT
```

## 📈 Scalability Considerations

### 1. Horizontal Scaling
- Stateless API сервисы
- Load balancing между инстансами
- Database connection pooling
- Cache layer (Redis)

### 2. Performance Optimization
- Async/await для I/O операций
- Connection pooling для внешних API
- Caching стратегии
- Background task processing

### 3. Resource Management
- Memory-efficient data processing
- Connection limits для внешних API
- Rate limiting для защиты от перегрузки
- Circuit breakers для resilience

## 🔄 Development Workflow

### 1. Code Organization
```
Модульная структура:
├── Сервисы с четкими интерфейсами
├── Dependency injection
├── Error handling patterns
└── Testing strategies
```

### 2. Quality Assurance
```
QA Process:
├── Unit tests (pytest)
├── Integration tests
├── API tests
├── Frontend tests (Jest)
└── E2E tests
```

### 3. CI/CD Pipeline
```
Deployment Pipeline:
├── Code commit → GitHub
├── Automated tests
├── Docker image build
├── Cloud deployment
└── Health checks
```

## 📚 API Documentation

### 1. OpenAPI/Swagger
- Автоматическая генерация документации
- Interactive API explorer
- Schema validation

### 2. WebSocket API
```
WebSocket Events:
├── connection_established
├── analysis_started/progress/completed/failed
├── task_update
├── system_alert
└── user_message
```

## 🎯 Future Enhancements

### 1. Planned Features
- Machine Learning model integration
- Advanced analytics dashboard
- Multi-language support
- Mobile app development

### 2. Technical Improvements
- GraphQL API layer
- Event sourcing implementation
- Advanced caching strategies
- Performance monitoring enhancements

---

**Документация обновлена:** 2025-06-26  
**Версия системы:** 1.1.0-dev  
**Статус:** В разработке
