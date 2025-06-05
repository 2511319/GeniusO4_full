# GeniusO4 Full

## Быстрый старт

1. Скопируйте `.env.example` в нужный файл окружения:
   ```bash
   cp .env.example .env.dev
   ```
   Аналогично создайте `.env.docker` и `.env.prod`, подставив свои значения.
   В файле окружения можно задать `DEFAULT_SYMBOL` и `DEFAULT_QUOTE` – базовую
   и котируемую валюту по умолчанию.
2. Запустите сервер вручную (из каталога `api`):
   ```bash
   python -m uvicorn app:app --reload
   ```
   или воспользуйтесь `python run.py --mode dev` либо `docker-compose up --build`.
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
Все ответы от API сохраняются в папку `frontend/dev_logs` для упрощения отладки.

### Типовой сценарий

1. Запустите `python run.py --mode dev` для одновременного старта FastAPI и Dash-интерфейса.
2. В другой вкладке запустите `npm run dev` в каталоге `frontend`.
3. Откройте `http://localhost:5173`, введите тикер и JWT‑токен и нажмите `Load`.
4. Выбирайте нужные индикаторы на графике чекбоксами.

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

Поле `symbol` может содержать пару целиком (`BTCUSDT`) или только базовый
актив (`BTC`). В последнем случае котируемая валюта берётся из переменной
`DEFAULT_QUOTE` (по умолчанию `USD`).

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

## Индикаторы

API поддерживает следующие индикаторы:

MACD, RSI, OBV, ATR, ADX, Stochastic_Oscillator, Volume,
Bollinger_Bands, Ichimoku_Cloud, Parabolic_SAR, VWAP,
Moving_Average_Envelopes, support_resistance_levels, trend_lines,
unfinished_zones, imbalances, fibonacci_analysis,
elliott_wave_analysis, structural_edge, candlestick_patterns,
divergence_analysis, fair_value_gaps, gap_analysis,
psychological_levels, anomalous_candles, price_prediction,
recommendations

## Тестирование и сборка

Проверить синтаксис Python:

```bash
python -m py_compile $(git ls-files '*.py')
```

Собрать фронтенд:

```bash
cd frontend
npm install
npm run build
```

Запустить тесты:

```bash
pytest                # проверка API
cd frontend && npm test
```

Для запуска в Docker или продакшн‑режиме используйте:

```bash
python run.py --mode docker      # локально через Docker
./deploy.sh                      # деплой в Cloud Run
```

## Деплой

Скрипт `deploy.sh` собирает образы и разворачивает сервисы в Google Cloud Run. Перед запуском создайте `.env.prod` и заполните переменные `GCP_PROJECT_ID` и `GCP_REGION`.

```bash
./deploy.sh
```

После деплоя UI доступен по адресу, указанному в выводе `gcloud run deploy`.

При клонировании репозитория не используйте опцию `--depth`, чтобы сохранялась полная история коммитов.

