#!/bin/bash

# Скрипт для ручного развертывания ChartGenius в Google Cloud Run
# Проект: chartgenius-444017

set -e

PROJECT_ID="chartgenius-444017"
REGION="us-central1"
COMMIT_SHA=$(git rev-parse --short HEAD)

echo "🚀 Ручное развертывание ChartGenius в Google Cloud Run"
echo "📋 Проект: $PROJECT_ID"
echo "🌍 Регион: $REGION"
echo "🔖 Коммит: $COMMIT_SHA"

# Устанавливаем проект
gcloud config set project $PROJECT_ID

# Функция для сборки и развертывания сервиса
deploy_service() {
    local service_name=$1
    local dockerfile_path=$2
    local service_port=$3
    local memory=$4
    local cpu=$5
    local max_instances=$6
    local secrets=$7
    local env_vars=$8
    
    echo ""
    echo "🔨 Сборка и развертывание $service_name..."
    
    # Сборка образа
    echo "📦 Сборка Docker образа..."
    gcloud builds submit \
        --tag gcr.io/$PROJECT_ID/$service_name:$COMMIT_SHA \
        --dockerfile $dockerfile_path \
        .
    
    # Развертывание в Cloud Run
    echo "🚀 Развертывание в Cloud Run..."
    gcloud run deploy $service_name \
        --image gcr.io/$PROJECT_ID/$service_name:$COMMIT_SHA \
        --region $REGION \
        --platform managed \
        --allow-unauthenticated \
        --port $service_port \
        --memory $memory \
        --cpu $cpu \
        --max-instances $max_instances \
        $secrets \
        $env_vars
    
    echo "✅ $service_name развернут успешно"
}

# Проверяем, что секреты существуют
echo "🔐 Проверка секретов..."
required_secrets=("JWT_SECRET_KEY" "TELEGRAM_BOT_TOKEN" "OPENAI_API_KEY")
for secret in "${required_secrets[@]}"; do
    if ! gcloud secrets describe $secret >/dev/null 2>&1; then
        echo "❌ Секрет $secret не найден. Запустите scripts/setup_gcp.sh"
        exit 1
    fi
done
echo "✅ Все необходимые секреты найдены"

# Развертывание Backend API
deploy_service \
    "chartgenius-api" \
    "backend/Dockerfile" \
    "8000" \
    "1Gi" \
    "1" \
    "10" \
    "--set-secrets=JWT_SECRET_KEY=JWT_SECRET_KEY:latest,TELEGRAM_BOT_TOKEN=TELEGRAM_BOT_TOKEN:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest,CRYPTOCOMPARE_API_KEY=CRYPTOCOMPARE_API_KEY:latest" \
    "--set-env-vars=LLM_PROVIDER=openai,DEFAULT_SYMBOL=BTCUSDT,LOCAL_TESTING=false"

# Получаем URL API для настройки других сервисов
API_URL=$(gcloud run services describe chartgenius-api --region=$REGION --format="value(status.url)")
echo "📡 API URL: $API_URL"

# Развертывание Frontend
echo ""
echo "🔨 Сборка Frontend с API URL..."
gcloud builds submit \
    --tag gcr.io/$PROJECT_ID/chartgenius-frontend:$COMMIT_SHA \
    --dockerfile frontend/Dockerfile \
    --build-arg VITE_API_URL=$API_URL \
    --build-arg VITE_TELEGRAM_BOT_USERNAME=Chart_Genius_bot \
    .

gcloud run deploy chartgenius-frontend \
    --image gcr.io/$PROJECT_ID/chartgenius-frontend:$COMMIT_SHA \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 80 \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 5

FRONTEND_URL=$(gcloud run services describe chartgenius-frontend --region=$REGION --format="value(status.url)")
echo "🌐 Frontend URL: $FRONTEND_URL"

# Развертывание Telegram Bot
deploy_service \
    "chartgenius-bot" \
    "bot/Dockerfile" \
    "8080" \
    "512Mi" \
    "1" \
    "5" \
    "--set-secrets=JWT_SECRET_KEY=JWT_SECRET_KEY:latest,TELEGRAM_BOT_TOKEN=TELEGRAM_BOT_TOKEN:latest" \
    "--set-env-vars=API_URL=$API_URL,WEBAPP_URL=$FRONTEND_URL"

BOT_URL=$(gcloud run services describe chartgenius-bot --region=$REGION --format="value(status.url)")
echo "🤖 Bot URL: $BOT_URL"

echo ""
echo "🎉 Развертывание завершено!"
echo ""
echo "📋 Сводка развертывания:"
echo "• API:      $API_URL"
echo "• Frontend: $FRONTEND_URL"
echo "• Bot:      $BOT_URL"
echo ""
echo "📝 Следующие шаги:"
echo "1. Настройте webhook для Telegram бота:"
echo "   curl -X POST \"https://api.telegram.org/bot\$TELEGRAM_BOT_TOKEN/setWebhook\" \\"
echo "        -H \"Content-Type: application/json\" \\"
echo "        -d '{\"url\": \"$BOT_URL/\$TELEGRAM_BOT_TOKEN\"}'"
echo ""
echo "2. Настройте команды бота:"
echo "   curl -X POST \"https://api.telegram.org/bot\$TELEGRAM_BOT_TOKEN/setMyCommands\" \\"
echo "        -H \"Content-Type: application/json\" \\"
echo "        -d '{\"commands\": [{\"command\": \"start\", \"description\": \"Начать работу с ботом\"}]}'"
echo ""
echo "3. Протестируйте приложение:"
echo "   • Откройте $FRONTEND_URL"
echo "   • Отправьте /start боту в Telegram"
echo ""
