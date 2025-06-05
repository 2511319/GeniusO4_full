# Разделение Frontend и Backend

Этот репозиторий изначально содержит Python‑фронтенд на Dash (`ui/`) и FastAPI‑бекенд (`api/`).
Для более гибкого интерфейса можно вынести клиентскую часть в современный JS‑фреймворк.

## Предлагаемый стек

- **Backend** – FastAPI остаётся без изменений.
- **Frontend** – React + Vite (`frontend/` каталог).
- **Графики** – библиотека [lightweight-charts](https://github.com/tradingview/lightweight-charts) от TradingView.

## Запуск прототипа фронтенда

```bash
cd frontend
npm install
npm run dev
```

По умолчанию дев‑сервер доступен на `http://localhost:5173` и проксирует запросы `/api` к FastAPI.

Директория теперь содержит прототип со входными полями "Тикер", "Интервал" и "Количество свечей". При нажатии **Анализ** выполняется POST `/api/analyze` и данные строятся в TradingView Lightweight Charts.
