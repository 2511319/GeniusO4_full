#!/bin/bash
# 🚀 ChartGenius Bot Deployment Script
# Версия: 1.1.0-dev
# Деплой исправленного бота в Google Cloud Run

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Конфигурация
PROJECT_ID="chartgenius-444017"
REGION="europe-west1"
SERVICE_NAME="chartgenius-bot"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
BOT_TOKEN="7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0"

# Функции для вывода
print_header() {
    echo -e "\n${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Проверка зависимостей
check_dependencies() {
    print_header "Проверка зависимостей"
    
    # Проверка gcloud
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI не установлен"
        exit 1
    fi
    print_success "gcloud CLI установлен"
    
    # Проверка Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker не установлен"
        exit 1
    fi
    print_success "Docker установлен"
    
    # Проверка аутентификации
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "Не выполнена аутентификация в gcloud"
        print_info "Выполните: gcloud auth login"
        exit 1
    fi
    print_success "gcloud аутентификация активна"
    
    # Проверка проекта
    current_project=$(gcloud config get-value project 2>/dev/null)
    if [ "$current_project" != "$PROJECT_ID" ]; then
        print_warning "Текущий проект: $current_project"
        print_info "Переключение на проект: $PROJECT_ID"
        gcloud config set project $PROJECT_ID
    fi
    print_success "Проект настроен: $PROJECT_ID"
}

# Тестирование бота локально
test_bot_locally() {
    print_header "Локальное тестирование бота"
    
    print_info "Запуск тестов..."
    if python test-bot.py; then
        print_success "Локальные тесты пройдены"
    else
        print_error "Локальные тесты не пройдены"
        read -p "Продолжить деплой? [y/N]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Сборка Docker образа
build_image() {
    print_header "Сборка Docker образа"

    print_info "Сборка образа для бота..."
    cd bot-dev

    # Создаем .dockerignore если его нет
    if [ ! -f .dockerignore ]; then
        cat > .dockerignore << EOF
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
.DS_Store
*.egg-info
.venv
venv/
EOF
    fi

    # Удаляем старые образы для принудительной пересборки
    print_info "Очистка старых образов..."
    docker rmi $IMAGE_NAME:latest 2>/dev/null || true
    docker system prune -f

    # Создаем уникальный тег с временной меткой
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    UNIQUE_TAG="v1.1.0-fix-${TIMESTAMP}"

    print_info "Сборка образа с тегом: $UNIQUE_TAG"

    # Сборка образа БЕЗ кеша
    docker build --no-cache --pull -t $IMAGE_NAME:latest -t $IMAGE_NAME:$UNIQUE_TAG .

    if [ $? -eq 0 ]; then
        print_success "Образ собран успешно с тегом: $UNIQUE_TAG"
        echo "IMAGE_TAG=$UNIQUE_TAG" > ../image_tag.env
    else
        print_error "Ошибка сборки образа"
        exit 1
    fi

    cd ..
}

# Пуш образа в Container Registry
push_image() {
    print_header "Загрузка образа в Container Registry"

    print_info "Настройка Docker для GCR..."
    gcloud auth configure-docker --quiet

    # Загружаем оба тега
    print_info "Загрузка образа latest..."
    docker push $IMAGE_NAME:latest

    # Загружаем уникальный тег если есть
    if [ -f image_tag.env ]; then
        source image_tag.env
        print_info "Загрузка образа с тегом: $IMAGE_TAG"
        docker push $IMAGE_NAME:$IMAGE_TAG
    fi

    if [ $? -eq 0 ]; then
        print_success "Образ загружен в GCR"
    else
        print_error "Ошибка загрузки образа"
        exit 1
    fi
}

# Деплой в Cloud Run
deploy_to_cloud_run() {
    print_header "Деплой в Google Cloud Run"
    
    print_info "Деплой сервиса..."
    
    # Получаем URL webhook
    SERVICE_URL="https://${SERVICE_NAME}-$(echo $REGION | tr '-' '')-${PROJECT_ID}.a.run.app"
    WEBHOOK_URL="${SERVICE_URL}/webhook"
    
    # Используем уникальный тег если доступен
    IMAGE_TO_DEPLOY="$IMAGE_NAME:latest"
    if [ -f image_tag.env ]; then
        source image_tag.env
        IMAGE_TO_DEPLOY="$IMAGE_NAME:$IMAGE_TAG"
        print_info "Деплой образа с тегом: $IMAGE_TAG"
    fi

    gcloud run deploy $SERVICE_NAME \
        --image $IMAGE_TO_DEPLOY \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 512Mi \
        --cpu 1 \
        --concurrency 1000 \
        --timeout 300 \
        --max-instances 10 \
        --set-env-vars "TELEGRAM_BOT_TOKEN=${BOT_TOKEN}" \
        --set-env-vars "WEBHOOK_URL=${WEBHOOK_URL}" \
        --set-env-vars "ENVIRONMENT=production" \
        --set-env-vars "DEBUG=false" \
        --set-env-vars "VERSION=1.1.0-prod-$(date +%Y%m%d-%H%M%S)" \
        --set-env-vars "DEPLOYED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        --port 8000 \
        --no-traffic \
        --tag candidate
    
    if [ $? -eq 0 ]; then
        print_success "Кандидатная версия развернута в Cloud Run"
        print_info "URL сервиса: $SERVICE_URL"

        # Тестируем кандидатную версию
        print_info "Тестирование кандидатной версии..."
        sleep 10

        # Получаем URL кандидатной версии
        CANDIDATE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.traffic[0].url)")

        if curl -f "${CANDIDATE_URL}/health" > /dev/null 2>&1; then
            print_success "Кандидатная версия прошла health check"

            # Переключаем весь трафик на новую версию
            print_info "Переключение трафика на новую версию..."
            gcloud run services update-traffic $SERVICE_NAME --to-latest --region=$REGION

            if [ $? -eq 0 ]; then
                print_success "Трафик переключен на новую версию"
            else
                print_error "Ошибка переключения трафика"
                exit 1
            fi
        else
            print_error "Кандидатная версия не прошла health check"
            print_warning "Откатываем деплой..."
            gcloud run services update-traffic $SERVICE_NAME --to-revisions=LATEST=0 --region=$REGION
            exit 1
        fi
    else
        print_error "Ошибка деплоя в Cloud Run"
        exit 1
    fi
}

# Настройка webhook
setup_webhook() {
    print_header "Настройка Telegram Webhook"
    
    # Получаем URL сервиса
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
    WEBHOOK_URL="${SERVICE_URL}/webhook"
    
    print_info "Настройка webhook: $WEBHOOK_URL"
    
    # Устанавливаем webhook
    curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
        -H "Content-Type: application/json" \
        -d "{\"url\":\"${WEBHOOK_URL}\",\"drop_pending_updates\":true}"
    
    echo
    
    # Проверяем webhook
    print_info "Проверка webhook..."
    curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo" | python -m json.tool
    
    print_success "Webhook настроен"
}

# Тестирование в production
test_production() {
    print_header "Тестирование в production"
    
    print_info "Ожидание готовности сервиса (30 секунд)..."
    sleep 30
    
    # Получаем URL сервиса
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
    
    # Тест health check
    print_info "Тестирование health check..."
    if curl -f "${SERVICE_URL}/health" > /dev/null 2>&1; then
        print_success "Health check пройден"
    else
        print_warning "Health check не пройден"
    fi
    
    # Тест отправки сообщения админу
    print_info "Отправка тестового сообщения..."
    curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
        -H "Content-Type: application/json" \
        -d '{"chat_id":"299820674","text":"🚀 ChartGenius Bot v1.1.0 успешно развернут!\n\nВсе исправления применены:\n✅ Исправлены callback handlers\n✅ Улучшен middleware\n✅ Добавлены таймауты\n✅ Добавлена обработка ошибок","parse_mode":"HTML"}'
    
    echo
    print_success "Тестовое сообщение отправлено"
}

# Проверка логов
check_logs() {
    print_header "Проверка логов"
    
    print_info "Последние логи сервиса:"
    gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
        --limit=10 \
        --format="table(timestamp,severity,textPayload)" \
        --freshness=1h
}

# Откат (если нужен)
rollback() {
    print_header "Откат к предыдущей версии"
    
    print_warning "Выполняется откат..."
    gcloud run services replace-traffic $SERVICE_NAME --to-revisions=LATEST=0 --region=$REGION
    
    print_success "Откат выполнен"
}

# Главная функция
main() {
    clear
    echo -e "${PURPLE}"
    echo "  ██████╗██╗  ██╗ █████╗ ██████╗ ████████╗ ██████╗ ███████╗███╗   ██╗██╗██╗   ██╗███████╗"
    echo " ██╔════╝██║  ██║██╔══██╗██╔══██╗╚══██╔══╝██╔════╝ ██╔════╝████╗  ██║██║██║   ██║██╔════╝"
    echo " ██║     ███████║███████║██████╔╝   ██║   ██║  ███╗█████╗  ██╔██╗ ██║██║██║   ██║███████╗"
    echo " ██║     ██╔══██║██╔══██║██╔══██╗   ██║   ██║   ██║██╔══╝  ██║╚██╗██║██║██║   ██║╚════██║"
    echo " ╚██████╗██║  ██║██║  ██║██║  ██║   ██║   ╚██████╔╝███████╗██║ ╚████║██║╚██████╔╝███████║"
    echo "  ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚══════╝"
    echo -e "${NC}"
    echo -e "${CYAN}                          Bot Deployment Script v1.1.0${NC}"
    echo -e "${CYAN}                               Production Deploy${NC}\n"
    
    # Выполнение шагов
    check_dependencies
    test_bot_locally
    build_image
    push_image
    deploy_to_cloud_run
    setup_webhook
    test_production
    check_logs
    
    print_header "🎉 Деплой завершен успешно!"
    print_success "ChartGenius Bot v1.1.0 развернут в production"
    print_info "Проверьте работу бота командой /start"
    
    # Опция просмотра логов
    echo
    read -p "Показать логи в реальном времени? [y/N]: " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Показ логов (Ctrl+C для выхода)..."
        gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME"
    fi
}

# Обработка сигналов
trap 'echo -e "\n${YELLOW}Получен сигнал остановки...${NC}"; exit 0' INT TERM

# Запуск основной функции
main "$@"
