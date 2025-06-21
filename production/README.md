# ChartGenius Production Deployment

Продакшн-готовая версия системы ChartGenius для развертывания в Google Cloud Platform.

## 🚀 Архитектура

- **Backend**: FastAPI + Python 3.10
- **Frontend**: React 18 + Vite + Material-UI
- **Bot**: Telegram Bot (python-telegram-bot)
- **Database**: Google Cloud Firestore
- **Secrets**: Google Cloud Secret Manager
- **Deployment**: Google Cloud Run (europe-west1)

## 📋 Предварительные требования

1. **Google Cloud Project** с включенными API:
   - Cloud Run API
   - Container Registry API
   - Secret Manager API
   - Firestore API

2. **Google Cloud CLI** установлен и настроен:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Docker** установлен для локальной сборки

## 🔐 Настройка секретов

Создайте секреты в Google Cloud Secret Manager:

```bash
# OpenAI API Key
echo "your-openai-api-key" | gcloud secrets create openai-api-key --data-file=-

# JWT Secret Key
echo "your-jwt-secret-key" | gcloud secrets create jwt-secret-key --data-file=-

# CryptoCompare API Key
echo "your-cryptocompare-api-key" | gcloud secrets create cryptocompare-api-key --data-file=-

# Telegram Bot Token
echo "your-telegram-bot-token" | gcloud secrets create telegram-bot-token --data-file=-
```

## 🛠️ Развертывание

### Быстрое развертывание

```bash
# Установите переменные окружения
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="europe-west1"

# Запустите скрипт развертывания
./deploy-production.sh
```

### Пошаговое развертывание

1. **Сборка образов**:
   ```bash
   docker build -t gcr.io/$GCP_PROJECT_ID/chartgenius-api:v1.0.0 -f production/backend/Dockerfile .
   docker build -t gcr.io/$GCP_PROJECT_ID/chartgenius-frontend:v1.0.0 -f production/frontend/Dockerfile .
   docker build -t gcr.io/$GCP_PROJECT_ID/chartgenius-bot:v1.0.0 -f production/bot/Dockerfile .
   ```

2. **Загрузка в Container Registry**:
   ```bash
   docker push gcr.io/$GCP_PROJECT_ID/chartgenius-api:v1.0.0
   docker push gcr.io/$GCP_PROJECT_ID/chartgenius-frontend:v1.0.0
   docker push gcr.io/$GCP_PROJECT_ID/chartgenius-bot:v1.0.0
   ```

3. **Развертывание сервисов**:
   ```bash
   # API Backend
   gcloud run deploy chartgenius-api \
     --image gcr.io/$GCP_PROJECT_ID/chartgenius-api:v1.0.0 \
     --platform managed \
     --region $GCP_REGION \
     --allow-unauthenticated \
     --memory 1Gi \
     --cpu 1 \
     --max-instances 10 \
     --set-secrets="OPENAI_API_KEY=openai-api-key:latest,JWT_SECRET_KEY=jwt-secret-key:latest,CRYPTOCOMPARE_API_KEY=cryptocompare-api-key:latest"

   # Frontend
   gcloud run deploy chartgenius-frontend \
     --image gcr.io/$GCP_PROJECT_ID/chartgenius-frontend:v1.0.0 \
     --platform managed \
     --region $GCP_REGION \
     --allow-unauthenticated \
     --memory 512Mi \
     --cpu 1 \
     --max-instances 5

   # Telegram Bot
   gcloud run deploy chartgenius-bot \
     --image gcr.io/$GCP_PROJECT_ID/chartgenius-bot:v1.0.0 \
     --platform managed \
     --region $GCP_REGION \
     --no-allow-unauthenticated \
     --memory 512Mi \
     --cpu 1 \
     --min-instances 1 \
     --max-instances 1 \
     --set-secrets="TELEGRAM_BOT_TOKEN=telegram-bot-token:latest"
   ```

## 🔍 Мониторинг

- **Логи**: Google Cloud Logging
- **Метрики**: Google Cloud Monitoring
- **Health Checks**: `/health` endpoint для каждого сервиса

## 🔧 Конфигурация

### Переменные окружения

- `GCP_PROJECT_ID`: ID проекта Google Cloud
- `GCP_REGION`: Регион развертывания (europe-west1)
- `ENVIRONMENT`: production
- `DEBUG_LOGGING`: false
- `ADMIN_TELEGRAM_ID`: 299820674

### Версионирование

Все образы помечены версиями в формате `v1.0.0`. При обновлении увеличивайте версию.

## 🚨 Безопасность

- Все секреты хранятся в Google Cloud Secret Manager
- CORS настроен только для продакшн доменов
- Отключено debug логирование
- Включена аутентификация для всех API endpoints

## 📞 Поддержка

При проблемах с развертыванием проверьте:
1. Логи Cloud Run сервисов
2. Настройки IAM ролей
3. Доступность секретов в Secret Manager
