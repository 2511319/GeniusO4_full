# ChartGenius

Этот репозиторий содержит backend на FastAPI и клиент на React.

## Структура проекта

- `backend` — серверные функции на FastAPI.
- `frontend` — клиентское приложение на React.

## Запуск

### Dev-режим

Установите зависимости и запустите приложения:

```bash
pip install -r backend/requirements.txt
npm install
uvicorn backend.app:app --reload
npm run dev
```

### Docker

```bash
docker-compose up --build
```

### Prod

Для продакшена используется скрипт `deploy.sh`. Он читает переменные из `.env.prod`.

```bash
./deploy.sh
```

## Тестирование

Backend:

```bash
pytest
```

Frontend:

```bash
npm test
```
