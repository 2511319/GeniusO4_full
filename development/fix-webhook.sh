#!/bin/bash
# 🔧 ChartGenius Bot Webhook Fix Script
# Версия: 1.1.0-dev
# Принудительное исправление webhook настроек

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Конфигурация
PROJECT_ID="chartgenius-444017"
REGION="europe-west1"
SERVICE_NAME="chartgenius-bot"
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

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Получение текущего статуса webhook
check_current_webhook() {
    print_header "Проверка текущего webhook"
    
    print_info "Получение информации о webhook..."
    WEBHOOK_INFO=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo")
    
    echo "$WEBHOOK_INFO" | python3 -m json.tool
    
    # Извлекаем URL
    CURRENT_URL=$(echo "$WEBHOOK_INFO" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['result'].get('url', ''))")
    PENDING_UPDATES=$(echo "$WEBHOOK_INFO" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['result'].get('pending_update_count', 0))")
    LAST_ERROR=$(echo "$WEBHOOK_INFO" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['result'].get('last_error_message', ''))")
    
    if [ -n "$CURRENT_URL" ]; then
        print_info "Текущий webhook URL: $CURRENT_URL"
    else
        print_warning "Webhook URL не установлен"
    fi
    
    if [ "$PENDING_UPDATES" -gt 0 ]; then
        print_warning "Ожидающих обновлений: $PENDING_UPDATES"
    fi
    
    if [ -n "$LAST_ERROR" ]; then
        print_error "Последняя ошибка: $LAST_ERROR"
    fi
}

# Удаление текущего webhook
remove_webhook() {
    print_header "Удаление текущего webhook"
    
    print_info "Удаление webhook..."
    RESULT=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/deleteWebhook" \
        -H "Content-Type: application/json" \
        -d '{"drop_pending_updates": true}')
    
    echo "$RESULT" | python3 -m json.tool
    
    SUCCESS=$(echo "$RESULT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('ok', False))")
    
    if [ "$SUCCESS" = "True" ]; then
        print_success "Webhook удален успешно"
    else
        print_error "Ошибка удаления webhook"
        exit 1
    fi
    
    # Ждем немного
    print_info "Ожидание 5 секунд..."
    sleep 5
}

# Получение URL сервиса
get_service_url() {
    print_header "Получение URL сервиса"
    
    print_info "Получение URL Cloud Run сервиса..."
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>/dev/null)
    
    if [ -z "$SERVICE_URL" ]; then
        print_error "Не удалось получить URL сервиса"
        print_info "Проверьте что сервис $SERVICE_NAME развернут в регионе $REGION"
        exit 1
    fi
    
    print_success "URL сервиса: $SERVICE_URL"
    
    # Формируем webhook URL
    WEBHOOK_URL="${SERVICE_URL}/webhook"
    print_info "Webhook URL: $WEBHOOK_URL"
}

# Тестирование доступности сервиса
test_service_availability() {
    print_header "Тестирование доступности сервиса"
    
    # Тест health check
    print_info "Тестирование health check..."
    HEALTH_URL="${SERVICE_URL}/health"
    
    if curl -f -s "$HEALTH_URL" > /dev/null; then
        print_success "Health check прошел успешно"
    else
        print_error "Health check не прошел"
        print_warning "Сервис может быть недоступен"
        
        read -p "Продолжить установку webhook? [y/N]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Тест webhook endpoint
    print_info "Тестирование webhook endpoint..."
    
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d '{"test": "ping"}')
    
    if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "400" ] || [ "$HTTP_STATUS" = "405" ]; then
        print_success "Webhook endpoint отвечает (HTTP $HTTP_STATUS)"
    else
        print_warning "Webhook endpoint вернул HTTP $HTTP_STATUS"
    fi
}

# Установка нового webhook
set_new_webhook() {
    print_header "Установка нового webhook"
    
    print_info "Установка webhook URL: $WEBHOOK_URL"
    
    # Генерируем случайный secret token
    SECRET_TOKEN=$(openssl rand -hex 16)
    
    RESULT=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
        -H "Content-Type: application/json" \
        -d "{
            \"url\": \"${WEBHOOK_URL}\",
            \"drop_pending_updates\": true,
            \"secret_token\": \"${SECRET_TOKEN}\",
            \"max_connections\": 40,
            \"allowed_updates\": [\"message\", \"callback_query\", \"inline_query\"]
        }")
    
    echo "$RESULT" | python3 -m json.tool
    
    SUCCESS=$(echo "$RESULT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('ok', False))")
    
    if [ "$SUCCESS" = "True" ]; then
        print_success "Webhook установлен успешно"
        print_info "Secret token: $SECRET_TOKEN"
        
        # Сохраняем secret token в переменную окружения Cloud Run
        print_info "Обновление переменных окружения..."
        gcloud run services update $SERVICE_NAME \
            --region=$REGION \
            --set-env-vars "WEBHOOK_SECRET=${SECRET_TOKEN}" \
            --quiet
        
        if [ $? -eq 0 ]; then
            print_success "Secret token добавлен в переменные окружения"
        else
            print_warning "Не удалось обновить переменные окружения"
        fi
    else
        print_error "Ошибка установки webhook"
        exit 1
    fi
}

# Проверка нового webhook
verify_webhook() {
    print_header "Проверка нового webhook"
    
    print_info "Ожидание 10 секунд для стабилизации..."
    sleep 10
    
    print_info "Получение информации о webhook..."
    WEBHOOK_INFO=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo")
    
    echo "$WEBHOOK_INFO" | python3 -m json.tool
    
    # Проверяем что URL установлен корректно
    NEW_URL=$(echo "$WEBHOOK_INFO" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['result'].get('url', ''))")
    PENDING_UPDATES=$(echo "$WEBHOOK_INFO" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['result'].get('pending_update_count', 0))")
    
    if [ "$NEW_URL" = "$WEBHOOK_URL" ]; then
        print_success "Webhook URL установлен корректно"
    else
        print_error "Webhook URL не соответствует ожидаемому"
        print_info "Ожидаемый: $WEBHOOK_URL"
        print_info "Фактический: $NEW_URL"
    fi
    
    if [ "$PENDING_UPDATES" -eq 0 ]; then
        print_success "Нет ожидающих обновлений"
    else
        print_info "Ожидающих обновлений: $PENDING_UPDATES"
    fi
}

# Отправка тестового сообщения
send_test_message() {
    print_header "Отправка тестового сообщения"
    
    TEST_MESSAGE="🔧 <b>Webhook исправлен!</b>

Время: $(date '+%Y-%m-%d %H:%M:%S')

✅ Webhook URL обновлен
✅ Secret token установлен  
✅ Pending updates очищены
✅ Переменные окружения обновлены

Проверьте работу команды /start"

    print_info "Отправка тестового сообщения админу..."
    
    RESULT=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
        -H "Content-Type: application/json" \
        -d "{
            \"chat_id\": \"299820674\",
            \"text\": \"${TEST_MESSAGE}\",
            \"parse_mode\": \"HTML\"
        }")
    
    SUCCESS=$(echo "$RESULT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('ok', False))")
    
    if [ "$SUCCESS" = "True" ]; then
        print_success "Тестовое сообщение отправлено"
    else
        print_error "Ошибка отправки тестового сообщения"
        echo "$RESULT" | python3 -m json.tool
    fi
}

# Главная функция
main() {
    clear
    echo -e "${BLUE}"
    echo "🔧 ИСПРАВЛЕНИЕ TELEGRAM WEBHOOK"
    echo "================================"
    echo -e "${NC}"
    echo -e "${CYAN}Проект: $PROJECT_ID${NC}"
    echo -e "${CYAN}Сервис: $SERVICE_NAME${NC}"
    echo -e "${CYAN}Регион: $REGION${NC}"
    echo
    
    # Выполняем все шаги
    check_current_webhook
    remove_webhook
    get_service_url
    test_service_availability
    set_new_webhook
    verify_webhook
    send_test_message
    
    print_header "🎉 Webhook исправлен успешно!"
    print_success "Все операции завершены"
    print_info "Проверьте работу бота командой /start в @Chart_Genius_bot"
}

# Обработка сигналов
trap 'echo -e "\n${YELLOW}Получен сигнал остановки...${NC}"; exit 0' INT TERM

# Запуск основной функции
main "$@"
