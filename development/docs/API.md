# 🔌 ChartGenius API Documentation
**Версия: 1.1.0-dev**  
**Дата: 2025-06-26**

## 📋 Обзор

ChartGenius API предоставляет RESTful endpoints для анализа криптовалют, управления системой и real-time уведомлений через WebSocket.

**Base URL (Development):** `http://localhost:8001`  
**WebSocket URL:** `ws://localhost:8001/ws/{user_id}`

## 🔐 Аутентификация

### JWT Authentication
```http
Authorization: Bearer <jwt_token>
```

### Telegram WebApp Authentication
```javascript
// Frontend integration
window.Telegram.WebApp.initData
```

## 📊 Analysis API

### Синхронный анализ
```http
POST /api/analysis/analyze
Content-Type: application/json

{
  "symbol": "BTCUSDT",
  "interval": "4h",
  "layers": ["RSI", "MACD", "MA_20"],
  "limit": 500
}
```

**Response:**
```json
{
  "figure": {...},
  "analysis": "Детальный анализ...",
  "ohlc": [...],
  "indicators": ["RSI", "MACD"]
}
```

### Асинхронный анализ
```http
POST /api/analyze/async
Content-Type: application/json

{
  "symbol": "BTCUSDT",
  "interval": "4h",
  "indicators": ["RSI", "MACD", "MA_20"],
  "user_id": "user123"
}
```

**Response:**
```json
{
  "task_id": "task_abc123",
  "status": "started",
  "message": "Асинхронный анализ BTCUSDT запущен"
}
```

### Статус задачи
```http
GET /api/analyze/status/{task_id}
```

**Response:**
```json
{
  "task_id": "task_abc123",
  "status": "PROCESSING",
  "progress": 65,
  "message": "Генерация AI анализа...",
  "result": null,
  "error": null
}
```

### Результат анализа
```http
GET /api/analyze/result/{task_id}
```

### Отмена анализа
```http
DELETE /api/analyze/cancel/{task_id}
```

## 🛠️ Admin API

### Управление промптами

#### Загрузка промпта
```http
POST /api/llm/prompt/upload
Content-Type: application/json

{
  "prompt_type": "technical_analysis",
  "version": "1.1",
  "prompt_text": "Вы эксперт по техническому анализу...",
  "description": "Обновленный промпт для технического анализа",
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 4000
  }
}
```

#### Список всех промптов
```http
GET /api/llm/prompts
```

**Response:**
```json
{
  "success": true,
  "prompts": {
    "technical_analysis": {
      "prompt_type": "technical_analysis",
      "active_version": "1.1",
      "versions": {
        "1.0": {...},
        "1.1": {...}
      },
      "updated_at": "2025-06-26T10:00:00Z"
    }
  }
}
```

#### Метаданные промпта
```http
GET /api/llm/prompts/{prompt_type}
```

#### Содержимое активного промпта
```http
GET /api/llm/prompts/{prompt_type}/content
```

#### Содержимое версии промпта
```http
GET /api/llm/prompts/{prompt_type}/versions/{version}
```

#### Активация версии
```http
PUT /api/llm/prompts/{prompt_type}/activate/{version}
```

#### Удаление версии
```http
DELETE /api/llm/prompts/{prompt_type}/versions/{version}
```

### Управление рыночными данными

#### Статус бирж
```http
GET /api/market/exchanges
```

**Response:**
```json
{
  "success": true,
  "exchanges": {
    "timestamp": "2025-06-26T10:00:00Z",
    "sources": {
      "coingecko": {
        "status": "healthy",
        "last_check": "2025-06-26T10:00:00Z"
      },
      "ccxt_binance": {
        "status": "healthy",
        "response_time": 0.15,
        "error_rate": 0.02
      }
    }
  }
}
```

#### Символы биржи
```http
GET /api/market/symbols/{exchange}
```

#### Тикер символа
```http
GET /api/market/ticker/{symbol}?source=ccxt_binance
```

**Response:**
```json
{
  "success": true,
  "symbol": "BTC/USDT",
  "ticker": {
    "last": 47500.00,
    "bid": 47450.00,
    "ask": 47550.00,
    "volume": 1000.50,
    "change": 500.00,
    "percentage": 1.06,
    "source": "binance"
  }
}
```

#### Общее состояние системы
```http
GET /api/market/health
```

**Response:**
```json
{
  "success": true,
  "market_data": {...},
  "ccxt_exchanges": {...},
  "system": {
    "version": "1.1.0-dev",
    "environment": "development",
    "services": {
      "redis": "healthy",
      "metrics": "healthy"
    }
  }
}
```

## 📈 Metrics API

### Prometheus метрики
```http
GET /metrics
Content-Type: text/plain
```

**Response:**
```
# HELP chartgenius_api_requests_total Total API requests
# TYPE chartgenius_api_requests_total counter
chartgenius_api_requests_total{method="GET",endpoint="/api/analysis",status_code="200"} 150

# HELP chartgenius_llm_requests_total Total LLM requests
# TYPE chartgenius_llm_requests_total counter
chartgenius_llm_requests_total{provider="openai",model="gpt-4",status="success"} 45
```

## 🔌 WebSocket API

### Подключение
```javascript
const ws = new WebSocket('ws://localhost:8001/ws/user123');
```

### События от сервера

#### Установка соединения
```json
{
  "type": "connection_established",
  "data": {
    "message": "WebSocket соединение установлено",
    "user_id": "user123",
    "server_time": "2025-06-26T10:00:00Z"
  },
  "timestamp": "2025-06-26T10:00:00Z"
}
```

#### Начало анализа
```json
{
  "type": "analysis_started",
  "data": {
    "task_id": "task_abc123",
    "symbol": "BTCUSDT",
    "message": "Анализ запущен"
  },
  "timestamp": "2025-06-26T10:00:00Z",
  "task_id": "task_abc123"
}
```

#### Прогресс анализа
```json
{
  "type": "analysis_progress",
  "data": {
    "task_id": "task_abc123",
    "progress": 65,
    "status": "Генерация AI анализа...",
    "current_step": "llm_analysis"
  },
  "timestamp": "2025-06-26T10:00:00Z",
  "task_id": "task_abc123"
}
```

#### Завершение анализа
```json
{
  "type": "analysis_completed",
  "data": {
    "task_id": "task_abc123",
    "symbol": "BTCUSDT",
    "message": "Анализ завершен",
    "action": {
      "type": "view_result",
      "url": "/analysis/result/task_abc123"
    }
  },
  "timestamp": "2025-06-26T10:00:00Z",
  "task_id": "task_abc123"
}
```

#### Ошибка анализа
```json
{
  "type": "analysis_failed",
  "data": {
    "task_id": "task_abc123",
    "symbol": "BTCUSDT",
    "message": "Ошибка получения данных",
    "error": "Network timeout"
  },
  "timestamp": "2025-06-26T10:00:00Z",
  "task_id": "task_abc123"
}
```

### События от клиента

#### Подписка на задачу
```json
{
  "type": "subscribe_task",
  "data": {
    "task_id": "task_abc123"
  }
}
```

#### Отписка от задачи
```json
{
  "type": "unsubscribe_task",
  "data": {
    "task_id": "task_abc123"
  }
}
```

#### Ping
```json
{
  "type": "ping",
  "data": {
    "timestamp": "2025-06-26T10:00:00Z"
  }
}
```

## 🚨 Error Handling

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error

### Error Response Format
```json
{
  "detail": "Error description",
  "error_code": "INVALID_SYMBOL",
  "timestamp": "2025-06-26T10:00:00Z"
}
```

### Common Error Codes
- `INVALID_SYMBOL` - Неподдерживаемый символ
- `INVALID_INTERVAL` - Неподдерживаемый интервал
- `TASK_NOT_FOUND` - Задача не найдена
- `PROMPT_NOT_FOUND` - Промпт не найден
- `RATE_LIMIT_EXCEEDED` - Превышен лимит запросов

## 📝 Request/Response Examples

### Полный пример анализа
```bash
# 1. Запуск асинхронного анализа
curl -X POST http://localhost:8001/api/analyze/async \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "interval": "4h",
    "indicators": ["RSI", "MACD"],
    "user_id": "user123"
  }'

# Response: {"task_id": "task_abc123", "status": "started"}

# 2. Подписка на WebSocket уведомления
# ws://localhost:8001/ws/user123
# Send: {"type": "subscribe_task", "data": {"task_id": "task_abc123"}}

# 3. Получение результата
curl http://localhost:8001/api/analyze/result/task_abc123
```

## 🔧 Development Tools

### Swagger UI
```
http://localhost:8001/docs
```

### ReDoc
```
http://localhost:8001/redoc
```

### Health Check
```bash
curl http://localhost:8001/health
```

---

**Документация обновлена:** 2025-06-26  
**Версия API:** 1.1.0-dev  
**Статус:** В разработке
