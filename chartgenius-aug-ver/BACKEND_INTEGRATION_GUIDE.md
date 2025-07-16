# ChartGenius - Руководство по интеграции с бэкендом

## Обзор проекта

ChartGenius Augment Agent Version - это современный фронтенд для торгового приложения, построенный на React + TypeScript + Vite. Проект готов к интеграции с бэкендом и содержит все необходимые компоненты для полнофункционального торгового интерфейса.

## Архитектура фронтенда

### Основные компоненты
- **Chart.tsx** - Основной компонент графика с использованием lightweight-charts
- **AnalysisPanel.tsx** - Панель технического анализа
- **Controls.tsx** - Панель управления индикаторами и настройками
- **ControlMenu.tsx** - Меню управления графиком
- **ElementDetailsPanel.tsx** - Панель деталей выбранных элементов

### Структура данных
Фронтенд ожидает данные в следующих форматах (см. `src/data.ts`):

```typescript
// Данные свечей
interface CandleData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

// Данные индикаторов
interface IndicatorData {
  time: string;
  value: number;
}

// Данные анализа
interface AnalysisData {
  symbol: string;
  timeframe: string;
  indicators: {
    [key: string]: IndicatorData[];
  };
  analysis: {
    trend: 'bullish' | 'bearish' | 'neutral';
    strength: number;
    signals: Signal[];
  };
}
```

## API Endpoints, которые должен предоставить бэкенд

### 1. Получение данных графика
```
GET /api/chart-data
Query Parameters:
- symbol: string (например, "BTCUSDT")
- timeframe: string (например, "1h", "4h", "1d")
- from: timestamp
- to: timestamp

Response:
{
  "data": CandleData[],
  "symbol": string,
  "timeframe": string
}
```

### 2. Получение данных индикаторов
```
GET /api/indicators
Query Parameters:
- symbol: string
- timeframe: string
- indicators: string[] (массив названий индикаторов)
- from: timestamp
- to: timestamp

Response:
{
  "indicators": {
    "sma_20": IndicatorData[],
    "rsi": IndicatorData[],
    "macd": IndicatorData[],
    // ... другие индикаторы
  }
}
```

### 3. Получение технического анализа
```
GET /api/analysis
Query Parameters:
- symbol: string
- timeframe: string

Response:
{
  "analysis": {
    "trend": "bullish" | "bearish" | "neutral",
    "strength": number,
    "signals": [
      {
        "type": "buy" | "sell" | "hold",
        "strength": number,
        "description": string,
        "indicator": string
      }
    ],
    "support_levels": number[],
    "resistance_levels": number[],
    "fibonacci_levels": {
      "0": number,
      "23.6": number,
      "38.2": number,
      "50": number,
      "61.8": number,
      "100": number
    }
  }
}
```

### 4. WebSocket для реального времени
```
WebSocket: /ws/chart-data
Message format:
{
  "type": "price_update",
  "symbol": string,
  "data": CandleData
}

{
  "type": "indicator_update",
  "symbol": string,
  "indicator": string,
  "data": IndicatorData
}
```

## Конфигурация CORS

Бэкенд должен разрешить CORS для следующих origins:
- `http://localhost:5173` (dev server)
- `http://localhost:4173` (preview server)
- Ваш production домен

Пример конфигурации для FastAPI:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Переменные окружения

Создайте файл `.env` в корне проекта:
```
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
```

## Поддерживаемые индикаторы

Фронтенд готов к работе со следующими индикаторами:
- **Трендовые**: SMA, EMA, Bollinger Bands
- **Осцилляторы**: RSI, MACD, Stochastic
- **Объемные**: Volume, OBV
- **Уровни**: Support/Resistance, Fibonacci
- **Паттерны**: Candlestick patterns

## Структура ответов для индикаторов

### Moving Averages (SMA, EMA)
```json
{
  "sma_20": [
    {"time": "2024-01-01T00:00:00Z", "value": 45000.50}
  ]
}
```

### RSI
```json
{
  "rsi": [
    {"time": "2024-01-01T00:00:00Z", "value": 65.5}
  ]
}
```

### MACD
```json
{
  "macd": [
    {
      "time": "2024-01-01T00:00:00Z",
      "macd": 150.5,
      "signal": 140.2,
      "histogram": 10.3
    }
  ]
}
```

### Bollinger Bands
```json
{
  "bollinger": [
    {
      "time": "2024-01-01T00:00:00Z",
      "upper": 46000,
      "middle": 45000,
      "lower": 44000
    }
  ]
}
```

## Аутентификация (если требуется)

Если требуется аутентификация, фронтенд готов к работе с JWT токенами:

```typescript
// Заголовки запросов
headers: {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
}
```

## Обработка ошибок

Бэкенд должен возвращать ошибки в следующем формате:
```json
{
  "error": {
    "code": "INVALID_SYMBOL",
    "message": "Символ не найден",
    "details": "Символ BTCUSDT не поддерживается"
  }
}
```

## Тестирование интеграции

1. Запустите бэкенд на `http://localhost:8000`
2. Убедитесь, что все endpoints доступны
3. Запустите фронтенд: `npm run dev`
4. Проверьте работу в браузере на `http://localhost:5173`

## Известные ограничения

- **Fibonacci индикатор**: Отображение уровней Фибоначчи имеет известную проблему и отложено на следующий этап разработки
- **Реальное время**: WebSocket подключение реализовано, но требует тестирования с реальным бэкендом

## Развертывание

### Development
```bash
npm install
npm run dev
```

### Production
```bash
npm install
npm run build
npm run preview
```

## Контакты и поддержка

Проект готов к интеграции. При возникновении вопросов обращайтесь к документации в папке `docs/` или к коду компонентов.

---

**Статус проекта**: ✅ Готов к интеграции с бэкендом
**Последнее обновление**: 2025-01-16
**Версия**: Augment Agent v1.0
