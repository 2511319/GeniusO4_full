# GeniusO4 Full

## Быстрый старт

1. Скопируйте .env.example → .env и заполните ключи.
2. Запустите:
   ```
   docker-compose up --build
   ```
3. Откройте:
   - UI: http://localhost:8050
   - Health: http://localhost:8000/health

## Структура

- api/       — FastAPI + сервисы
- ui/        — Dash-интерфейс (Python)
- frontend/  — прототип React-клиента
- configs/   — настройки
- docker-compose.yml
- .github/workflows/ci.yml

## Запуск React-клиента

```bash
cd frontend
npm install
npm run dev
```

Дев-сервер доступен на `http://localhost:5173` и проксирует запросы `/api` к FastAPI.

## Работа с API `/api/analyze`

Пример запроса:

```json
{
  "symbol": "BTCUSDT",
  "interval": "4h",
  "limit": 144,
  "indicators": ["MACD", "RSI"]
}
```

Если список индикаторов пустой, строятся все доступные слои. В ответе приходят:

```json
{
  "figure": {},
  "analysis": {},
  "ohlc": [ {"Open Time": "...", "Open": 0, ... } ],
  "indicators": ["RSI", "MACD", "MA_50", ...]
}
```

Для авторизации используйте JWT‑токен:

```
Authorization: Bearer <JWT>
```

В React-клиенте токен можно ввести в поле — он сохраняется в `localStorage` и будет автоматически подставляться в запросы. Интерфейс позволяет включать и отключать отдельные слои графика чекбоксами.

