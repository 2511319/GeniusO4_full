#!/bin/bash

# Скрипт настройки Google Cloud Platform для ChartGenius
# Проект: chartgenius-444017

set -e

PROJECT_ID="chartgenius-444017"
REGION="us-central1"

echo "🚀 Настройка Google Cloud Platform для проекта $PROJECT_ID"

# Проверяем, что gcloud установлен
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI не установлен. Установите Google Cloud SDK."
    exit 1
fi

# Устанавливаем проект по умолчанию
echo "📋 Устанавливаем проект $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Включаем необходимые API
echo "🔧 Включаем необходимые API..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable monitoring.googleapis.com

echo "✅ API включены успешно"

# Создаем Firestore базу данных
echo "🗄️ Создаем Firestore базу данных..."
if ! gcloud firestore databases describe --region=$REGION 2>/dev/null; then
    gcloud firestore databases create --region=$REGION
    echo "✅ Firestore база данных создана"
else
    echo "ℹ️ Firestore база данных уже существует"
fi

# Функция для создания секрета
create_secret() {
    local secret_name=$1
    local secret_description=$2
    
    if ! gcloud secrets describe $secret_name 2>/dev/null; then
        echo "🔐 Создаем секрет $secret_name..."
        echo "PLACEHOLDER_VALUE" | gcloud secrets create $secret_name \
            --data-file=- \
            --labels=project=chartgenius,environment=production
        echo "✅ Секрет $secret_name создан (требуется обновление значения)"
    else
        echo "ℹ️ Секрет $secret_name уже существует"
    fi
}

# Создаем секреты
echo "🔐 Создаем секреты в Secret Manager..."
create_secret "JWT_SECRET_KEY" "JWT secret key for authentication"
create_secret "TELEGRAM_BOT_TOKEN" "Telegram bot token"
create_secret "OPENAI_API_KEY" "OpenAI API key for analysis"
create_secret "CRYPTOCOMPARE_API_KEY" "CryptoCompare API key for market data"

# Создаем сервисный аккаунт для GitHub Actions
echo "👤 Создаем сервисный аккаунт для CI/CD..."
SA_NAME="github-actions"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

if ! gcloud iam service-accounts describe $SA_EMAIL 2>/dev/null; then
    gcloud iam service-accounts create $SA_NAME \
        --display-name="GitHub Actions Service Account" \
        --description="Service account for GitHub Actions CI/CD"
    echo "✅ Сервисный аккаунт создан"
else
    echo "ℹ️ Сервисный аккаунт уже существует"
fi

# Назначаем роли сервисному аккаунту
echo "🔑 Назначаем роли сервисному аккаунту..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/run.developer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/cloudbuild.builds.builder"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/storage.admin"

echo "✅ Роли назначены"

# Создаем ключ для сервисного аккаунта
echo "🗝️ Создаем ключ для сервисного аккаунта..."
if [ ! -f "github-actions-key.json" ]; then
    gcloud iam service-accounts keys create github-actions-key.json \
        --iam-account=$SA_EMAIL
    echo "✅ Ключ создан: github-actions-key.json"
    echo "⚠️ Добавьте содержимое этого файла в GitHub Secrets как GCP_SA_KEY"
else
    echo "ℹ️ Ключ уже существует"
fi

# Создаем Cloud Build триггер (если нужно)
echo "🔨 Настройка Cloud Build..."
echo "ℹ️ Cloud Build триггер можно настроить через веб-интерфейс или GitHub Actions"

echo ""
echo "🎉 Настройка Google Cloud Platform завершена!"
echo ""
echo "📝 Следующие шаги:"
echo "1. Обновите секреты в Secret Manager:"
echo "   - JWT_SECRET_KEY: gcloud secrets versions add JWT_SECRET_KEY --data-file=-"
echo "   - TELEGRAM_BOT_TOKEN: gcloud secrets versions add TELEGRAM_BOT_TOKEN --data-file=-"
echo "   - OPENAI_API_KEY: gcloud secrets versions add OPENAI_API_KEY --data-file=-"
echo "   - CRYPTOCOMPARE_API_KEY: gcloud secrets versions add CRYPTOCOMPARE_API_KEY --data-file=-"
echo ""
echo "2. Добавьте в GitHub Secrets:"
echo "   - GCP_PROJECT_ID: $PROJECT_ID"
echo "   - GCP_SA_KEY: содержимое файла github-actions-key.json"
echo ""
echo "3. Настройте Firestore коллекции:"
echo "   - users (для пользователей Telegram)"
echo "   - subscriptions (для управления подписками)"
echo "   - analyses (для хранения результатов анализа с TTL 30 дней)"
echo ""
echo "4. Запустите деплой через GitHub Actions или вручную"
echo ""
