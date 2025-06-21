#!/usr/bin/env bash
# production/setup-secrets.sh
# Скрипт для настройки секретов в Google Cloud Secret Manager

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
check_env() {
    if [ -z "$GCP_PROJECT_ID" ]; then
        log_error "GCP_PROJECT_ID не установлен"
        exit 1
    fi
    
    log_info "Проект: $GCP_PROJECT_ID"
}

# Проверка gcloud
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        log_error "Google Cloud CLI не установлен"
        exit 1
    fi
    
    gcloud config set project $GCP_PROJECT_ID
    log_success "Google Cloud CLI настроен"
}

# Включение Secret Manager API
enable_api() {
    log_info "Включение Secret Manager API..."
    gcloud services enable secretmanager.googleapis.com
    log_success "Secret Manager API включен"
}

# Функция для создания секрета
create_secret() {
    local secret_name=$1
    local description=$2
    
    if gcloud secrets describe $secret_name &> /dev/null; then
        log_warning "Секрет $secret_name уже существует"
        return 0
    fi
    
    log_info "Создание секрета: $secret_name"
    
    # Запрашиваем значение секрета
    echo -n "Введите значение для $secret_name ($description): "
    read -s secret_value
    echo
    
    if [ -z "$secret_value" ]; then
        log_error "Значение секрета не может быть пустым"
        return 1
    fi
    
    # Создаем секрет
    echo "$secret_value" | gcloud secrets create $secret_name --data-file=-
    log_success "Секрет $secret_name создан"
}

# Генерация JWT ключа
generate_jwt_key() {
    local secret_name="jwt-secret-key"
    
    if gcloud secrets describe $secret_name &> /dev/null; then
        log_warning "Секрет $secret_name уже существует"
        return 0
    fi
    
    log_info "Генерация JWT секретного ключа..."
    
    # Проверяем наличие openssl
    if command -v openssl &> /dev/null; then
        jwt_key=$(openssl rand -base64 32)
        echo "$jwt_key" | gcloud secrets create $secret_name --data-file=-
        log_success "JWT ключ сгенерирован и сохранен"
    else
        log_warning "OpenSSL не найден, создаем ключ вручную"
        create_secret $secret_name "JWT секретный ключ (минимум 32 символа)"
    fi
}

# Основная функция настройки
setup_secrets() {
    log_info "Настройка секретов для ChartGenius..."
    
    # OpenAI API Key
    create_secret "openai-api-key" "OpenAI API ключ (sk-...)"
    
    # JWT Secret Key (генерируем автоматически)
    generate_jwt_key
    
    # CryptoCompare API Key
    create_secret "cryptocompare-api-key" "CryptoCompare API ключ"
    
    # Telegram Bot Token
    create_secret "telegram-bot-token" "Telegram Bot токен (получен от @BotFather)"
    
    log_success "Все секреты настроены!"
}

# Проверка созданных секретов
verify_secrets() {
    log_info "Проверка созданных секретов..."
    
    secrets=("openai-api-key" "jwt-secret-key" "cryptocompare-api-key" "telegram-bot-token")
    
    for secret in "${secrets[@]}"; do
        if gcloud secrets describe $secret &> /dev/null; then
            log_success "✓ $secret"
        else
            log_error "✗ $secret - НЕ НАЙДЕН"
        fi
    done
}

# Настройка IAM ролей
setup_iam() {
    log_info "Настройка IAM ролей для Cloud Run..."
    
    # Получаем номер проекта
    project_number=$(gcloud projects describe $GCP_PROJECT_ID --format="value(projectNumber)")
    
    # Сервисный аккаунт Cloud Run по умолчанию
    service_account="$project_number-compute@developer.gserviceaccount.com"
    
    # Добавляем роль Secret Manager Secret Accessor
    gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
        --member="serviceAccount:$service_account" \
        --role="roles/secretmanager.secretAccessor" \
        --quiet
    
    log_success "IAM роли настроены"
}

# Показать инструкции
show_instructions() {
    log_info "Секреты успешно настроены!"
    echo
    log_info "Следующие шаги:"
    echo "1. Убедитесь, что все API ключи действительны"
    echo "2. Запустите развертывание: ./deploy-production.sh"
    echo "3. Проверьте логи сервисов после развертывания"
    echo
    log_info "Для просмотра секретов используйте:"
    echo "gcloud secrets list"
    echo
    log_warning "ВАЖНО: Никогда не передавайте секреты через незащищенные каналы!"
}

# Главная функция
main() {
    echo "🔐 Настройка секретов ChartGenius для Google Cloud"
    echo "=================================================="
    echo
    
    check_env
    check_gcloud
    enable_api
    setup_secrets
    verify_secrets
    setup_iam
    show_instructions
}

# Запуск скрипта
main "$@"
