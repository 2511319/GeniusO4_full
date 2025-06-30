# Telegram Integration

Документация по интеграции с Telegram Mini-App и ботом.

## Архитектура

### Компоненты

1. **Telegram Bot** (`bot/bot.py`) - основной бот для команд и управления
2. **Telegram WebApp Middleware** (`backend/middleware/telegram_webapp.py`) - аутентификация через Mini-App
3. **RBAC System** (`backend/auth/dependencies.py`) - система ролей и прав доступа
4. **API Routers** - новые эндпоинты для админов, модераторов и watchlist

### Роли пользователей

- **user** - базовая роль, доступ к основным функциям
- **premium** - доступ к watchlist и расширенным функциям
- **vip** - все функции premium + приоритетная поддержка
- **moderator** - модерация контента, баны пользователей
- **admin** - полный доступ ко всем функциям

## Telegram Bot

### Команды

#### Для всех пользователей:
- `/start` - главное меню с кнопками
- `/help` - список доступных команд
- `/watch BTC,ETH` - обновить watch-лист
- `/settings lang=ru tz=UTC+3` - настройки

#### Для модераторов:
- `/ban @user_id 15` - забанить на 15 дней
- `/unban @user_id` - разбанить
- `/review <ulid> <reason>` - пометить анализ флагом

#### Для админов:
- `/setrole @user_id vip 60` - установить роль и подписку
- `/stats` - статистика пользователей
- `/broadcast <текст>` - рассылка всем пользователям
- `/gc` - очистка устаревших данных

### Запуск бота

```bash
# Локально
cd bot
python bot.py

# Docker
docker build -t chartgenius-bot -f bot/Dockerfile .
docker run -d --env-file .env chartgenius-bot
```

## API Endpoints

### Admin API (`/api/admin/`)

- `GET /stats` - статистика пользователей
- `POST /set_role` - установка роли пользователю
- `POST /broadcast` - создание рассылки
- `POST /gc` - очистка данных

### Moderator API (`/api/moderator/`)

- `POST /ban` - бан пользователя
- `POST /unban` - разбан пользователя
- `POST /review_flag` - пометка анализа флагом
- `GET /bans` - список активных банов
- `GET /flags` - список флагов

### Watchlist API (`/api/watch/`)

- `POST /set` - установить весь watchlist
- `GET /get` - получить watchlist
- `POST /add` - добавить символ
- `POST /remove` - удалить символ
- `DELETE /clear` - очистить watchlist

## Аутентификация

### Telegram WebApp

1. Пользователь открывает Mini-App в Telegram
2. Telegram передает `init_data` с подписанными данными пользователя
3. Backend валидирует подпись через `telegram-webapp-auth`
4. Создается или обновляется пользователь в Firestore
5. Возвращается JWT токен для дальнейших запросов

### JWT Tokens

- **WebApp Token** - создается на 10 минут для "Открыть в браузере"
- **Bot Token** - долгосрочный токен для бота

## Firestore Schema

```
users/{telegram_id}
  - username: string
  - first_name: string
  - last_name: string
  - role: string (user|premium|vip|moderator|admin)
  - created_at: timestamp
  - last_seen: timestamp

subscriptions/{telegram_id}
  - level: string (premium|vip)
  - expires_at: timestamp
  - created_at: timestamp

watchlists/{telegram_id}
  - symbols: array[string]
  - updated_at: timestamp

bans/{telegram_id}
  - moderator_id: string
  - reason: string
  - expires_at: timestamp
  - created_at: timestamp

flags/{analysis_ulid}
  - reason: string
  - flagged_by: string
  - ts: timestamp

analyses/{ulid}
  - owner_id: string
  - json_result: object
  - created_at: timestamp
  # TTL: 30 days

broadcast_queue/{id}
  - text: string
  - user_ids: array[string]
  - status: string (pending|sent|failed)
  - created_at: timestamp
```

## Cron Jobs

### Cloud Scheduler Jobs

1. **expire_subs** - ежедневно в 00:00 UTC
   ```bash
   python backend/jobs/expire_subs.py
   ```

2. **daily_digest** - ежедневно в 08:00 UTC
   ```bash
   python backend/jobs/daily_digest.py
   ```

3. **prune_flags** - еженедельно в воскресенье 02:00 UTC
   ```bash
   python backend/jobs/prune_flags.py
   ```

## Развертывание

### Google Cloud Run

```bash
# Сборка и деплой всех компонентов
./deploy.sh

# Только бот
gcloud run deploy chartgenius-bot \
  --image gcr.io/PROJECT_ID/chartgenius-bot:latest \
  --platform managed \
  --region europe-west1 \
  --set-env-vars "TELEGRAM_BOT_TOKEN=...,ADMIN_TELEGRAM_ID=299820674"
```

### Переменные окружения

```bash
# Обязательные
TELEGRAM_BOT_TOKEN=7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0
JWT_SECRET_KEY=your-secret-key
ADMIN_TELEGRAM_ID=299820674

# Опциональные
WEBAPP_URL=https://your-webapp-url.com
GCP_PROJECT_ID=your-project-id
GCP_REGION=europe-west1
```

## Тестирование

```bash
# Запуск тестов
pytest tests/test_watchlist.py
pytest tests/test_mod_ban.py
pytest tests/test_admin_stats.py

# Все тесты
pytest tests/
```
