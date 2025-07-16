# Технические требования к бэкенду

## Общие требования

### Технологический стек (рекомендуемый)
- **Python**: FastAPI или Django REST Framework
- **База данных**: PostgreSQL или MongoDB
- **Кэширование**: Redis
- **WebSocket**: FastAPI WebSocket или Socket.IO
- **Очереди**: Celery + Redis/RabbitMQ

### Производительность
- Время ответа API: < 200ms для основных endpoints
- WebSocket latency: < 50ms
- Поддержка до 1000 одновременных подключений
- Кэширование данных индикаторов на 1-5 минут

## Обязательные API endpoints

### 1. Данные графика
```
GET /api/chart-data
- Параметры: symbol, timeframe, from, to
- Лимит: до 1000 свечей за запрос
- Кэширование: 1 минута для завершенных свечей
```

### 2. Индикаторы
```
GET /api/indicators
- Поддержка множественных индикаторов в одном запросе
- Параметризация индикаторов (период, настройки)
- Кэширование: 1-5 минут в зависимости от таймфрейма
```

### 3. Технический анализ
```
GET /api/analysis
- Комплексный анализ тренда
- Сигналы покупки/продажи
- Уровни поддержки/сопротивления
- Обновление: каждые 5-15 минут
```

### 4. WebSocket
```
WS /ws/chart-data
- Подписка на символы
- Реальное время обновления цен
- Обновления индикаторов
- Heartbeat каждые 30 секунд
```

## Обязательные индикаторы

### Трендовые индикаторы
- **SMA** (Simple Moving Average) - периоды: 10, 20, 50, 100, 200
- **EMA** (Exponential Moving Average) - периоды: 12, 26, 50, 100
- **Bollinger Bands** - период: 20, отклонение: 2
- **Ichimoku Cloud** - стандартные настройки

### Осцилляторы
- **RSI** (Relative Strength Index) - период: 14
- **MACD** - быстрая: 12, медленная: 26, сигнальная: 9
- **Stochastic** - %K: 14, %D: 3
- **Williams %R** - период: 14

### Объемные индикаторы
- **Volume** - объем торгов
- **OBV** (On-Balance Volume)
- **Volume Profile** - распределение объема по ценам

### Уровни и паттерны
- **Support/Resistance** - автоматическое определение
- **Fibonacci Retracements** - уровни: 23.6%, 38.2%, 50%, 61.8%
- **Pivot Points** - классические уровни

## Структура базы данных

### Таблица свечей (OHLCV)
```sql
CREATE TABLE candles (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open DECIMAL(20,8) NOT NULL,
    high DECIMAL(20,8) NOT NULL,
    low DECIMAL(20,8) NOT NULL,
    close DECIMAL(20,8) NOT NULL,
    volume DECIMAL(20,8) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, timeframe, timestamp)
);

CREATE INDEX idx_candles_symbol_timeframe_timestamp 
ON candles(symbol, timeframe, timestamp);
```

### Таблица индикаторов
```sql
CREATE TABLE indicators (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    indicator_name VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    value JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, timeframe, indicator_name, timestamp)
);

CREATE INDEX idx_indicators_lookup 
ON indicators(symbol, timeframe, indicator_name, timestamp);
```

### Таблица анализа
```sql
CREATE TABLE analysis (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    trend VARCHAR(20) NOT NULL,
    strength INTEGER NOT NULL,
    signals JSONB NOT NULL,
    support_levels JSONB NOT NULL,
    resistance_levels JSONB NOT NULL,
    fibonacci_levels JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, timeframe, timestamp)
);
```

## Кэширование

### Redis структура
```
# Данные свечей
candles:{symbol}:{timeframe}:{timestamp} -> OHLCV data (TTL: 60s)

# Индикаторы
indicators:{symbol}:{timeframe}:{indicator}:{timestamp} -> value (TTL: 300s)

# Анализ
analysis:{symbol}:{timeframe} -> analysis data (TTL: 900s)

# Список символов
symbols:list -> array of symbols (TTL: 3600s)
```

## WebSocket протокол

### Подключение
```javascript
// Клиент подключается
ws://localhost:8000/ws/chart-data

// Сервер отправляет приветствие
{
  "type": "welcome",
  "message": "Connected to ChartGenius WebSocket"
}
```

### Подписка
```javascript
// Клиент подписывается
{
  "action": "subscribe",
  "symbol": "BTCUSDT",
  "timeframe": "1h"
}

// Сервер подтверждает
{
  "type": "subscribed",
  "symbol": "BTCUSDT",
  "timeframe": "1h"
}
```

### Обновления
```javascript
// Обновление цены
{
  "type": "price_update",
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "data": {...}
}

// Обновление индикатора
{
  "type": "indicator_update",
  "symbol": "BTCUSDT",
  "indicator": "rsi",
  "data": {...}
}
```

## Безопасность

### Аутентификация (опционально)
- JWT токены
- Refresh token механизм
- Rate limiting: 100 запросов/минуту на IP

### CORS настройки
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:4173",
    "https://yourdomain.com"
]
```

### Валидация данных
- Проверка символов на whitelist
- Валидация таймфреймов
- Ограничение диапазона дат
- Санитизация входных параметров

## Мониторинг и логирование

### Метрики
- Количество запросов по endpoints
- Время ответа API
- Количество WebSocket подключений
- Использование кэша (hit/miss ratio)

### Логирование
- Все API запросы с параметрами
- Ошибки с stack trace
- WebSocket подключения/отключения
- Обновления данных

## Развертывание

### Docker конфигурация
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment переменные
```env
DATABASE_URL=postgresql://user:pass@localhost/chartgenius
REDIS_URL=redis://localhost:6379
API_RATE_LIMIT=100
WEBSOCKET_MAX_CONNECTIONS=1000
LOG_LEVEL=INFO
```

## Тестирование

### Unit тесты
- Тестирование всех API endpoints
- Валидация форматов данных
- Тестирование индикаторов

### Integration тесты
- WebSocket подключения
- Кэширование
- База данных операции

### Load тесты
- 1000 одновременных WebSocket подключений
- 100 запросов/секунду к API
- Стресс тестирование индикаторов

## Примеры реализации

### FastAPI endpoint
```python
@app.get("/api/chart-data")
async def get_chart_data(
    symbol: str,
    timeframe: str,
    from_timestamp: int,
    to_timestamp: int
):
    # Валидация параметров
    # Проверка кэша
    # Запрос к базе данных
    # Возврат данных
    pass
```

### WebSocket handler
```python
@app.websocket("/ws/chart-data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Обработка подписок
    # Отправка обновлений
    pass
```

---

**Статус**: Готово к реализации
**Приоритет**: Высокий
**Срок реализации**: 2-3 недели
