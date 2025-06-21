# ChartGenius Production Deployment Guide

## 🎯 Обзор

Это руководство описывает полный процесс развертывания ChartGenius в продакшн на Google Cloud Platform.

## ✅ Предварительные требования

### 1. Google Cloud Project
- Создан проект в Google Cloud Console
- Включен биллинг
- Установлен Google Cloud CLI

### 2. Локальная среда
- Docker установлен и запущен
- Git настроен
- Bash/PowerShell для выполнения скриптов

### 3. API ключи
- OpenAI API ключ
- CryptoCompare API ключ  
- Telegram Bot токен (от @BotFather)

## 🚀 Пошаговое развертывание

### Шаг 1: Подготовка окружения

```bash
# Клонирование репозитория
git clone <repository-url>
cd chartgenius

# Переход в продакшн директорию
cd production

# Установка переменных окружения
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="europe-west1"
```

### Шаг 2: Аутентификация в Google Cloud

```bash
# Вход в Google Cloud
gcloud auth login

# Установка проекта по умолчанию
gcloud config set project $GCP_PROJECT_ID

# Проверка настроек
gcloud config list
```

### Шаг 3: Настройка секретов

```bash
# Автоматическая настройка секретов
chmod +x setup-secrets.sh
./setup-secrets.sh

# Или ручная настройка (см. SECRETS_SETUP.md)
```

### Шаг 4: Развертывание

```bash
# Полное развертывание
chmod +x deploy-production.sh
./deploy-production.sh

# Или пошаговое развертывание (см. ниже)
```

## 🔧 Пошаговое развертывание

Если автоматический скрипт не подходит, выполните шаги вручную:

### 1. Включение API

```bash
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable firestore.googleapis.com
```

### 2. Сборка образов

```bash
# Backend
docker build -t gcr.io/$GCP_PROJECT_ID/chartgenius-api:v1.0.0 \
  -f production/backend/Dockerfile .

# Frontend  
docker build -t gcr.io/$GCP_PROJECT_ID/chartgenius-frontend:v1.0.0 \
  -f production/frontend/Dockerfile .

# Bot
docker build -t gcr.io/$GCP_PROJECT_ID/chartgenius-bot:v1.0.0 \
  -f production/bot/Dockerfile .
```

### 3. Загрузка образов

```bash
# Настройка Docker для GCR
gcloud auth configure-docker

# Загрузка образов
docker push gcr.io/$GCP_PROJECT_ID/chartgenius-api:v1.0.0
docker push gcr.io/$GCP_PROJECT_ID/chartgenius-frontend:v1.0.0
docker push gcr.io/$GCP_PROJECT_ID/chartgenius-bot:v1.0.0
```

### 4. Развертывание сервисов

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
  --set-env-vars="GCP_PROJECT_ID=$GCP_PROJECT_ID,GCP_REGION=$GCP_REGION" \
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
  --set-env-vars="GCP_PROJECT_ID=$GCP_PROJECT_ID,GCP_REGION=$GCP_REGION" \
  --set-secrets="TELEGRAM_BOT_TOKEN=telegram-bot-token:latest"
```

## 🔍 Проверка развертывания

### 1. Получение URL сервисов

```bash
# API URL
gcloud run services describe chartgenius-api \
  --platform=managed --region=$GCP_REGION \
  --format='value(status.url)'

# Frontend URL  
gcloud run services describe chartgenius-frontend \
  --platform=managed --region=$GCP_REGION \
  --format='value(status.url)'
```

### 2. Проверка health endpoints

```bash
# API Health Check
curl https://your-api-url/health

# Frontend Health Check
curl https://your-frontend-url/health
```

### 3. Проверка логов

```bash
# Логи API
gcloud run logs read chartgenius-api --region=$GCP_REGION

# Логи Frontend
gcloud run logs read chartgenius-frontend --region=$GCP_REGION

# Логи Bot
gcloud run logs read chartgenius-bot --region=$GCP_REGION
```

## 🔄 Обновление

### Обновление с новой версией

```bash
# Установка новой версии
export VERSION="v1.1.0"

# Пересборка и загрузка образов
docker build -t gcr.io/$GCP_PROJECT_ID/chartgenius-api:$VERSION \
  -f production/backend/Dockerfile .
docker push gcr.io/$GCP_PROJECT_ID/chartgenius-api:$VERSION

# Обновление сервиса
gcloud run services update chartgenius-api \
  --image gcr.io/$GCP_PROJECT_ID/chartgenius-api:$VERSION \
  --region=$GCP_REGION
```

## 🚨 Откат

### Откат к предыдущей версии

```bash
# Просмотр ревизий
gcloud run revisions list --service=chartgenius-api --region=$GCP_REGION

# Откат к конкретной ревизии
gcloud run services update-traffic chartgenius-api \
  --to-revisions=REVISION_NAME=100 \
  --region=$GCP_REGION
```

## 📊 Мониторинг

### Настройка алертов

```bash
# Создание политики алертов для высокой нагрузки
gcloud alpha monitoring policies create --policy-from-file=monitoring/alert-policy.yaml
```

### Просмотр метрик

- Перейдите в Google Cloud Console
- Откройте Cloud Monitoring
- Выберите Cloud Run в ресурсах

## 🔧 Troubleshooting

### Частые проблемы

1. **Ошибка доступа к секретам**
   - Проверьте IAM роли сервисного аккаунта
   - Убедитесь, что секреты существуют

2. **Превышение лимитов памяти**
   - Увеличьте memory в конфигурации Cloud Run
   - Оптимизируйте код приложения

3. **Таймауты запросов**
   - Увеличьте timeout в конфигурации
   - Проверьте производительность внешних API

### Полезные команды

```bash
# Просмотр конфигурации сервиса
gcloud run services describe SERVICE_NAME --region=$GCP_REGION

# Просмотр активных ревизий
gcloud run revisions list --service=SERVICE_NAME --region=$GCP_REGION

# Просмотр трафика
gcloud run services describe SERVICE_NAME --region=$GCP_REGION \
  --format='value(status.traffic[].percent,status.traffic[].revisionName)'
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи сервисов
2. Убедитесь в корректности секретов
3. Проверьте статус Google Cloud сервисов
4. Обратитесь к документации Google Cloud Run
