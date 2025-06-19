# Инструкция по деплою GeniusO4 с Telegram интеграцией

## Предварительные требования

1. **Google Cloud Platform аккаунт** с активированным биллингом
2. **Telegram Bot Token** - создайте бота через @BotFather
3. **OpenAI API Key** для анализа
4. **CryptoCompare API Key** для получения данных

## 1. Настройка Google Cloud

### 1.1 Создание проекта
```bash
gcloud projects create geniuso4-project --name="GeniusO4"
gcloud config set project geniuso4-project
```

### 1.2 Включение необходимых API
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable firestore.googleapis.com
```

### 1.3 Создание секретов в Secret Manager
```bash
# JWT Secret Key
echo -n "your-super-secret-jwt-key-here" | gcloud secrets create JWT_SECRET_KEY --data-file=-

# Telegram Bot Token
echo -n "your-telegram-bot-token" | gcloud secrets create TELEGRAM_BOT_TOKEN --data-file=-

# OpenAI API Key
echo -n "your-openai-api-key" | gcloud secrets create OPENAI_API_KEY --data-file=-

# CryptoCompare API Key
echo -n "your-cryptocompare-api-key" | gcloud secrets create CRYPTOCOMPARE_API_KEY --data-file=-
```

## 2. Настройка Firestore

### 2.1 Создание базы данных Firestore
```bash
gcloud firestore databases create --region=us-central1
```

### 2.2 Создание коллекций
Создайте следующие коллекции в Firestore Console:
- `users` - для хранения пользователей Telegram
- `subscriptions` - для управления подписками
- `analyses` - для хранения результатов анализа

### 2.3 Настройка TTL для коллекции analyses
В Firestore Console настройте TTL policy для поля `created_at` в коллекции `analyses` на 30 дней.

## 3. Деплой сервисов в Cloud Run

### 3.1 Деплой Backend API
```bash
gcloud run deploy geniuso4-api \
  --source backend/ \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets="JWT_SECRET_KEY=JWT_SECRET_KEY:latest,TELEGRAM_BOT_TOKEN=TELEGRAM_BOT_TOKEN:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest,CRYPTOCOMPARE_API_KEY=CRYPTOCOMPARE_API_KEY:latest" \
  --set-env-vars="LLM_PROVIDER=openai,DEFAULT_SYMBOL=BTCUSDT"
```

### 3.2 Деплой Telegram Bot
```bash
gcloud run deploy geniuso4-bot \
  --source bot/ \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets="JWT_SECRET_KEY=JWT_SECRET_KEY:latest,TELEGRAM_BOT_TOKEN=TELEGRAM_BOT_TOKEN:latest" \
  --set-env-vars="API_URL=https://geniuso4-api-[hash]-uc.a.run.app,WEBAPP_URL=https://geniuso4-frontend-[hash]-uc.a.run.app"
```

### 3.3 Деплой Frontend
```bash
gcloud run deploy geniuso4-frontend \
  --source frontend/ \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="VITE_API_URL=https://geniuso4-api-[hash]-uc.a.run.app,VITE_TELEGRAM_BOT_USERNAME=your_bot_username"
```

## 4. Настройка Telegram Bot

### 4.1 Получение URL сервисов
```bash
# Получить URL API
gcloud run services describe geniuso4-api --region=us-central1 --format="value(status.url)"

# Получить URL Bot
gcloud run services describe geniuso4-bot --region=us-central1 --format="value(status.url)"

# Получить URL Frontend
gcloud run services describe geniuso4-frontend --region=us-central1 --format="value(status.url)"
```

### 4.2 Настройка webhook для бота
```bash
# Замените YOUR_BOT_TOKEN и BOT_SERVICE_URL на реальные значения
curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://BOT_SERVICE_URL/YOUR_BOT_TOKEN"}'
```

### 4.3 Настройка команд бота
```bash
curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setMyCommands" \
  -H "Content-Type: application/json" \
  -d '{"commands": [{"command": "start", "description": "Начать работу с ботом"}]}'
```

## 5. Настройка CI/CD

### 5.1 Настройка GitHub Actions
Добавьте следующие секреты в GitHub repository:
- `GCP_PROJECT_ID` - ID вашего GCP проекта
- `GCP_SA_KEY` - JSON ключ сервисного аккаунта с правами Cloud Run Developer

### 5.2 Создание сервисного аккаунта
```bash
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions"

gcloud projects add-iam-policy-binding geniuso4-project \
  --member="serviceAccount:github-actions@geniuso4-project.iam.gserviceaccount.com" \
  --role="roles/run.developer"

gcloud projects add-iam-policy-binding geniuso4-project \
  --member="serviceAccount:github-actions@geniuso4-project.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.builder"

# Создание ключа
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions@geniuso4-project.iam.gserviceaccount.com
```

## 6. Тестирование

### 6.1 Локальное тестирование
```bash
# Установка зависимостей
pip install -r backend/requirements.txt
pip install -r bot/requirements.txt

# Запуск тестов
pytest tests/

# Запуск с Docker Compose
docker-compose up --build
```

### 6.2 Проверка деплоя
1. Откройте URL frontend сервиса
2. Попробуйте войти через Telegram
3. Отправьте команду `/start` боту в Telegram
4. Проверьте получение анализа через бота

## 7. Мониторинг и логи

### 7.1 Просмотр логов
```bash
# Логи API
gcloud run services logs read geniuso4-api --region=us-central1

# Логи Bot
gcloud run services logs read geniuso4-bot --region=us-central1

# Логи Frontend
gcloud run services logs read geniuso4-frontend --region=us-central1
```

### 7.2 Мониторинг
Используйте Google Cloud Console для мониторинга:
- Cloud Run > Services
- Cloud Logging
- Cloud Monitoring

## 8. Обновление

### 8.1 Автоматическое обновление через GitHub
Просто сделайте push в main ветку - GitHub Actions автоматически задеплоит изменения.

### 8.2 Ручное обновление
```bash
# Обновление конкретного сервиса
gcloud run deploy geniuso4-api --source backend/ --region us-central1
```

## 9. Troubleshooting

### 9.1 Проблемы с аутентификацией
- Проверьте правильность TELEGRAM_BOT_TOKEN
- Убедитесь, что webhook настроен корректно
- Проверьте логи бота

### 9.2 Проблемы с API
- Проверьте секреты в Secret Manager
- Убедитесь, что Firestore настроен правильно
- Проверьте переменные окружения

### 9.3 Проблемы с подписками
- Проверьте коллекцию subscriptions в Firestore
- Убедитесь, что telegram_id правильно сохраняется

## 10. Безопасность

1. **Регулярно обновляйте секреты**
2. **Используйте IAM роли с минимальными правами**
3. **Включите аудит логирование**
4. **Настройте мониторинг безопасности**

---

После выполнения всех шагов у вас будет полностью рабочая система с Telegram интеграцией, развернутая в Google Cloud Run.
