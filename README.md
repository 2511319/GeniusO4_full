# GeniusO4 Full

## Быстрый старт

1. Скопируйте .env.example → .env и заполните ключи.
2. Запустите:
   ```
   docker-compose up --build
   ```
3. Откройте:
   - UI: http://localhost:8050 (Dash)
   - React-прототип: http://localhost:5173
   - Health: http://localhost:8000/health

## Структура

- api/       — FastAPI + сервисы
- ui/        — Dash-интерфейс (Python)
- frontend/  — прототип React-клиента на TradingView Lightweight Charts
- configs/   — настройки
- docker-compose.yml
- .github/workflows/ci.yml

### Запуск React-прототипа

```bash
cd frontend
npm install
npm run dev
```
