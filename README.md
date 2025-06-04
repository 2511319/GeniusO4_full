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

- api/      — FastAPI + сервисы
- ui/       — Dash-интерфейс
- configs/  — настройки
- docker-compose.yml
- .github/workflows/ci.yml


