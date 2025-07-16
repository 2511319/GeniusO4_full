# API Examples - Примеры запросов и ответов

## 1. Получение данных графика

### Запрос
```http
GET /api/chart-data?symbol=BTCUSDT&timeframe=1h&from=1704067200&to=1704153600
```

### Ответ
```json
{
  "success": true,
  "data": [
    {
      "time": "2024-01-01T00:00:00Z",
      "open": 44000.50,
      "high": 44500.75,
      "low": 43800.25,
      "close": 44200.00,
      "volume": 1250.75
    },
    {
      "time": "2024-01-01T01:00:00Z",
      "open": 44200.00,
      "high": 44800.00,
      "low": 44100.00,
      "close": 44650.50,
      "volume": 980.25
    }
  ],
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "total": 24
}
```

## 2. Получение индикаторов

### Запрос
```http
GET /api/indicators?symbol=BTCUSDT&timeframe=1h&indicators=sma_20,rsi,macd&from=1704067200&to=1704153600
```

### Ответ
```json
{
  "success": true,
  "indicators": {
    "sma_20": [
      {"time": "2024-01-01T00:00:00Z", "value": 44100.25},
      {"time": "2024-01-01T01:00:00Z", "value": 44150.75}
    ],
    "rsi": [
      {"time": "2024-01-01T00:00:00Z", "value": 65.5},
      {"time": "2024-01-01T01:00:00Z", "value": 68.2}
    ],
    "macd": [
      {
        "time": "2024-01-01T00:00:00Z",
        "macd": 150.5,
        "signal": 140.2,
        "histogram": 10.3
      },
      {
        "time": "2024-01-01T01:00:00Z",
        "macd": 165.8,
        "signal": 145.1,
        "histogram": 20.7
      }
    ]
  }
}
```

## 3. Технический анализ

### Запрос
```http
GET /api/analysis?symbol=BTCUSDT&timeframe=1h
```

### Ответ
```json
{
  "success": true,
  "analysis": {
    "symbol": "BTCUSDT",
    "timeframe": "1h",
    "timestamp": "2024-01-01T12:00:00Z",
    "trend": "bullish",
    "strength": 75,
    "signals": [
      {
        "type": "buy",
        "strength": 80,
        "description": "RSI показывает восходящий тренд",
        "indicator": "rsi",
        "price": 44650.50
      },
      {
        "type": "buy",
        "strength": 70,
        "description": "MACD пересек сигнальную линию вверх",
        "indicator": "macd",
        "price": 44650.50
      }
    ],
    "support_levels": [43800, 44000, 44200],
    "resistance_levels": [44800, 45000, 45200],
    "fibonacci_levels": {
      "0": 43800,
      "23.6": 44036.8,
      "38.2": 44182.4,
      "50": 44300,
      "61.8": 44417.6,
      "100": 44800
    },
    "volume_analysis": {
      "trend": "increasing",
      "average_volume": 1150.5,
      "current_volume": 1250.75
    }
  }
}
```

## 4. WebSocket сообщения

### Подключение
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chart-data');
```

### Подписка на символ
```json
{
  "action": "subscribe",
  "symbol": "BTCUSDT",
  "timeframe": "1h"
}
```

### Обновление цены
```json
{
  "type": "price_update",
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "data": {
    "time": "2024-01-01T12:00:00Z",
    "open": 44650.50,
    "high": 44750.00,
    "low": 44600.00,
    "close": 44720.25,
    "volume": 125.5
  }
}
```

### Обновление индикатора
```json
{
  "type": "indicator_update",
  "symbol": "BTCUSDT",
  "indicator": "rsi",
  "data": {
    "time": "2024-01-01T12:00:00Z",
    "value": 72.3
  }
}
```

## 5. Обработка ошибок

### Символ не найден
```json
{
  "success": false,
  "error": {
    "code": "SYMBOL_NOT_FOUND",
    "message": "Символ не найден",
    "details": "Символ INVALID не поддерживается"
  }
}
```

### Неверный таймфрейм
```json
{
  "success": false,
  "error": {
    "code": "INVALID_TIMEFRAME",
    "message": "Неверный таймфрейм",
    "details": "Поддерживаемые таймфреймы: 1m, 5m, 15m, 1h, 4h, 1d"
  }
}
```

### Превышен лимит запросов
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Превышен лимит запросов",
    "details": "Максимум 100 запросов в минуту"
  }
}
```

## 6. Дополнительные endpoints

### Получение списка символов
```http
GET /api/symbols
```

```json
{
  "success": true,
  "symbols": [
    {
      "symbol": "BTCUSDT",
      "name": "Bitcoin/USDT",
      "type": "crypto",
      "active": true
    },
    {
      "symbol": "ETHUSDT",
      "name": "Ethereum/USDT", 
      "type": "crypto",
      "active": true
    }
  ]
}
```

### Получение доступных таймфреймов
```http
GET /api/timeframes
```

```json
{
  "success": true,
  "timeframes": [
    {"value": "1m", "label": "1 минута"},
    {"value": "5m", "label": "5 минут"},
    {"value": "15m", "label": "15 минут"},
    {"value": "1h", "label": "1 час"},
    {"value": "4h", "label": "4 часа"},
    {"value": "1d", "label": "1 день"}
  ]
}
```

### Получение доступных индикаторов
```http
GET /api/indicators/list
```

```json
{
  "success": true,
  "indicators": [
    {
      "id": "sma_20",
      "name": "SMA 20",
      "category": "trend",
      "parameters": [
        {"name": "period", "type": "number", "default": 20}
      ]
    },
    {
      "id": "rsi",
      "name": "RSI",
      "category": "oscillator",
      "parameters": [
        {"name": "period", "type": "number", "default": 14}
      ]
    }
  ]
}
```

## 7. Конфигурация фронтенда

### .env файл
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
VITE_API_TIMEOUT=10000
VITE_WS_RECONNECT_INTERVAL=5000
```

### Настройка API клиента
```typescript
// src/api/config.ts
export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT) || 10000,
  headers: {
    'Content-Type': 'application/json',
  }
};
```

---

**Примечание**: Все примеры приведены для демонстрации ожидаемого формата данных. Реальная реализация может отличаться в зависимости от требований бэкенда.
