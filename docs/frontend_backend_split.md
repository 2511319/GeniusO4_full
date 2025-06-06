# Разделение Frontend и Backend

Изначально проект включал Python‑фронтенд на Dash (`ui/`) и FastAPI‑бекенд (`api/`).
Теперь интерфейс полностью перенесён на React, а каталог `ui/` удалён.

## Предлагаемый стек

- **Backend** – FastAPI остаётся без изменений.
- **Frontend** – React + Vite (`frontend/` каталог).
- **Графики** – библиотека [TradingView Lightweight Charts](https://github.com/tradingview/lightweight-charts).

## Запуск прототипа фронтенда

```bash
cd frontend
npm install
npm run dev
```

По умолчанию дев‑сервер доступен на `http://localhost:5173` и проксирует запросы `/api` к FastAPI.

Эта директория содержит минимальный пример вывода графика с фиктивными данными. Далее её можно расширять компонентами и логикой приложения.
