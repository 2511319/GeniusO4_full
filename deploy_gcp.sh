#!/bin/bash

# Скрипт для деплоя GeniusO4 в Google Cloud Run

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода цветного текста
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверяем, что gcloud установлен
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI не установлен. Установите его с https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Получаем текущий проект
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    print_error "Проект GCP не настроен. Выполните: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

print_status "Используется проект: $PROJECT_ID"

# Проверяем, что необходимые API включены
print_status "Проверка необходимых API..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Создаем секреты если они не существуют
print_status "Создание секретов..."

create_secret_if_not_exists() {
    local secret_name=$1
    local secret_value=$2
    
    if ! gcloud secrets describe $secret_name &>/dev/null; then
        echo -n "$secret_value" | gcloud secrets create $secret_name --data-file=-
        print_success "Секрет $secret_name создан"
    else
        print_warning "Секрет $secret_name уже существует"
    fi
}

# Используем предустановленные значения
JWT_SECRET_KEY="34sSDF542rf65EJ1kj"
TELEGRAM_BOT_TOKEN="7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0"
OPENAI_API_KEY="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"
CRYPTOCOMPARE_API_KEY="4f09e9d732eab748157e44a138d88ac9b686ac373437ec5211910e02c14b7c15"

# Создаем секреты
create_secret_if_not_exists "JWT_SECRET_KEY" "$JWT_SECRET_KEY"
create_secret_if_not_exists "TELEGRAM_BOT_TOKEN" "$TELEGRAM_BOT_TOKEN"
create_secret_if_not_exists "OPENAI_API_KEY" "$OPENAI_API_KEY"
create_secret_if_not_exists "CRYPTOCOMPARE_API_KEY" "$CRYPTOCOMPARE_API_KEY"

# Запускаем сборку
print_status "Запуск Cloud Build..."
gcloud builds submit --config cloudbuild.yaml .

print_success "Деплой завершен!"

# Получаем URL сервисов
print_status "Получение URL сервисов..."
API_URL=$(gcloud run services describe geniuso4-api --region=us-central1 --format="value(status.url)")
BOT_URL=$(gcloud run services describe geniuso4-bot --region=us-central1 --format="value(status.url)")
FRONTEND_URL=$(gcloud run services describe geniuso4-frontend --region=us-central1 --format="value(status.url)")

echo ""
print_success "🎉 Деплой успешно завершен!"
echo ""
echo "📊 Frontend: $FRONTEND_URL"
echo "🔧 Backend API: $API_URL"
echo "🤖 Telegram Bot: $BOT_URL"
echo "📚 API Docs: $API_URL/docs"
echo ""
print_status "Настройка webhook для Telegram бота..."
curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"$BOT_URL\"}"

echo ""
print_success "✅ Все готово! Откройте $FRONTEND_URL для начала работы"
