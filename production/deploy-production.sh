#!/usr/bin/env bash
# production/deploy-production.sh
# Скрипт развертывания ChartGenius в продакшн на Google Cloud Platform

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка переменных окружения
check_env_vars() {
    log_info "Проверка переменных окружения..."
    
    if [ -z "$GCP_PROJECT_ID" ]; then
        log_error "GCP_PROJECT_ID не установлен"
        exit 1
    fi
    
    if [ -z "$GCP_REGION" ]; then
        log_warning "GCP_REGION не установлен, используется europe-west1"
        export GCP_REGION="europe-west1"
    fi
    
    log_success "Переменные окружения проверены"
    log_info "Проект: $GCP_PROJECT_ID"
    log_info "Регион: $GCP_REGION"
}

# Проверка Google Cloud CLI
check_gcloud() {
    log_info "Проверка Google Cloud CLI..."
    
    if ! command -v gcloud &> /dev/null; then
        log_error "Google Cloud CLI не установлен"
        exit 1
    fi
    
    # Проверка аутентификации
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "Не выполнена аутентификация в Google Cloud"
        log_info "Выполните: gcloud auth login"
        exit 1
    fi
    
    # Установка проекта
    gcloud config set project $GCP_PROJECT_ID
    
    log_success "Google Cloud CLI готов"
}

# Проверка Docker
check_docker() {
    log_info "Проверка Docker..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker не установлен"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker daemon не запущен"
        exit 1
    fi
    
    log_success "Docker готов"
}

# Проверка секретов
check_secrets() {
    log_info "Проверка секретов в Secret Manager..."
    
    secrets=("openai-api-key" "jwt-secret-key" "cryptocompare-api-key" "telegram-bot-token")
    
    for secret in "${secrets[@]}"; do
        if ! gcloud secrets describe $secret &> /dev/null; then
            log_error "Секрет $secret не найден в Secret Manager"
            log_info "Создайте секрет: echo 'your-secret-value' | gcloud secrets create $secret --data-file=-"
            exit 1
        fi
    done
    
    log_success "Все секреты найдены"
}

# Включение необходимых API
enable_apis() {
    log_info "Включение необходимых Google Cloud API..."
    
    apis=(
        "run.googleapis.com"
        "containerregistry.googleapis.com"
        "secretmanager.googleapis.com"
        "firestore.googleapis.com"
        "logging.googleapis.com"
        "monitoring.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        log_info "Включение $api..."
        gcloud services enable $api
    done
    
    log_success "API включены"
}

# Сборка образов
build_images() {
    log_info "Сборка Docker образов..."
    
    VERSION=${VERSION:-"1.0.0"}
    
    # Backend
    log_info "Сборка backend образа..."
    docker build -t gcr.io/$GCP_PROJECT_ID/chartgenius-api:$VERSION \
        -f production/backend/Dockerfile .
    
    # Frontend
    log_info "Сборка frontend образа..."
    docker build -t gcr.io/$GCP_PROJECT_ID/chartgenius-frontend:$VERSION \
        -f production/frontend/Dockerfile .
    
    # Bot
    log_info "Сборка bot образа..."
    docker build -t gcr.io/$GCP_PROJECT_ID/chartgenius-bot:$VERSION \
        -f production/bot/Dockerfile .
    
    log_success "Образы собраны"
}

# Загрузка образов
push_images() {
    log_info "Загрузка образов в Container Registry..."
    
    VERSION=${VERSION:-"1.0.0"}
    
    # Настройка Docker для работы с GCR
    gcloud auth configure-docker --quiet
    
    # Загрузка образов
    docker push gcr.io/$GCP_PROJECT_ID/chartgenius-api:$VERSION
    docker push gcr.io/$GCP_PROJECT_ID/chartgenius-frontend:$VERSION
    docker push gcr.io/$GCP_PROJECT_ID/chartgenius-bot:$VERSION
    
    log_success "Образы загружены"
}

# Развертывание сервисов
deploy_services() {
    log_info "Развертывание сервисов в Cloud Run..."
    
    VERSION=${VERSION:-"1.0.0"}
    
    # Backend API
    log_info "Развертывание API backend..."
    gcloud run deploy chartgenius-api \
        --image gcr.io/$GCP_PROJECT_ID/chartgenius-api:$VERSION \
        --platform managed \
        --region $GCP_REGION \
        --allow-unauthenticated \
        --memory 1Gi \
        --cpu 1 \
        --max-instances 10 \
        --min-instances 0 \
        --concurrency 80 \
        --timeout 300 \
        --set-env-vars="GCP_PROJECT_ID=$GCP_PROJECT_ID,GCP_REGION=$GCP_REGION,ENVIRONMENT=production,ADMIN_TELEGRAM_ID=299820674" \
        --set-secrets="OPENAI_API_KEY=openai-api-key:latest,JWT_SECRET_KEY=jwt-secret-key:latest,CRYPTOCOMPARE_API_KEY=cryptocompare-api-key:latest" \
        --quiet
    
    # Получение URL API
    API_URL=$(gcloud run services describe chartgenius-api --platform=managed --region=$GCP_REGION --format='value(status.url)')
    log_info "API URL: $API_URL"
    
    # Frontend
    log_info "Развертывание frontend..."
    gcloud run deploy chartgenius-frontend \
        --image gcr.io/$GCP_PROJECT_ID/chartgenius-frontend:$VERSION \
        --platform managed \
        --region $GCP_REGION \
        --allow-unauthenticated \
        --memory 512Mi \
        --cpu 1 \
        --max-instances 5 \
        --min-instances 0 \
        --concurrency 100 \
        --timeout 60 \
        --set-env-vars="API_URL=$API_URL" \
        --quiet
    
    # Получение URL Frontend
    FRONTEND_URL=$(gcloud run services describe chartgenius-frontend --platform=managed --region=$GCP_REGION --format='value(status.url)')
    log_info "Frontend URL: $FRONTEND_URL"
    
    # Telegram Bot
    log_info "Развертывание Telegram бота..."
    gcloud run deploy chartgenius-bot \
        --image gcr.io/$GCP_PROJECT_ID/chartgenius-bot:$VERSION \
        --platform managed \
        --region $GCP_REGION \
        --no-allow-unauthenticated \
        --memory 512Mi \
        --cpu 1 \
        --min-instances 1 \
        --max-instances 1 \
        --concurrency 1 \
        --timeout 3600 \
        --set-env-vars="GCP_PROJECT_ID=$GCP_PROJECT_ID,GCP_REGION=$GCP_REGION,ENVIRONMENT=production,ADMIN_TELEGRAM_ID=299820674" \
        --set-secrets="TELEGRAM_BOT_TOKEN=telegram-bot-token:latest" \
        --quiet
    
    log_success "Сервисы развернуты"
    log_success "Frontend: $FRONTEND_URL"
    log_success "API: $API_URL"
}

# Проверка развертывания
verify_deployment() {
    log_info "Проверка развертывания..."
    
    # Проверка API
    API_URL=$(gcloud run services describe chartgenius-api --platform=managed --region=$GCP_REGION --format='value(status.url)')
    if curl -f "$API_URL/health" &> /dev/null; then
        log_success "API работает корректно"
    else
        log_error "API недоступен"
        exit 1
    fi
    
    # Проверка Frontend
    FRONTEND_URL=$(gcloud run services describe chartgenius-frontend --platform=managed --region=$GCP_REGION --format='value(status.url)')
    if curl -f "$FRONTEND_URL/health" &> /dev/null; then
        log_success "Frontend работает корректно"
    else
        log_error "Frontend недоступен"
        exit 1
    fi
    
    log_success "Развертывание успешно завершено!"
}

# Основная функция
main() {
    log_info "Начало развертывания ChartGenius в продакшн..."
    
    check_env_vars
    check_gcloud
    check_docker
    check_secrets
    enable_apis
    build_images
    push_images
    deploy_services
    verify_deployment
    
    log_success "🎉 ChartGenius успешно развернут в продакшн!"
    log_info "Не забудьте настроить домены и SSL сертификаты при необходимости"
}

# Запуск скрипта
main "$@"
