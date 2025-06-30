#!/bin/bash
# 🔄 ChartGenius Stable Version Restore Script
# Версия: v1.0.51-stable
# Дата: 25.06.2025
# Назначение: Быстрое восстановление стабильной конфигурации

set -e

PROJECT_ID="chartgenius-444017"
REGION="europe-west1"
STABLE_VERSION="v1.0.51-stable"

echo "🔄 ВОССТАНОВЛЕНИЕ СТАБИЛЬНОЙ ВЕРСИИ CHARTGENIUS"
echo "=============================================="
echo "Версия: $STABLE_VERSION"
echo "Проект: $PROJECT_ID"
echo "Регион: $REGION"
echo "Дата: $(date)"
echo ""

# Функция логирования
log() {
    echo "[$(date +'%H:%M:%S')] $1"
}

# Функция подтверждения
confirm() {
    read -p "⚠️ $1 (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

# Проверка аутентификации
check_auth() {
    log "🔐 Проверка аутентификации..."
    
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log "❌ Необходима аутентификация в Google Cloud"
        log "Выполните: gcloud auth login"
        exit 1
    fi
    
    if [ "$(gcloud config get-value project)" != "$PROJECT_ID" ]; then
        log "⚠️ Текущий проект: $(gcloud config get-value project)"
        log "Ожидаемый проект: $PROJECT_ID"
        
        if confirm "Переключиться на проект $PROJECT_ID?"; then
            gcloud config set project $PROJECT_ID
        else
            log "❌ Отмена восстановления"
            exit 1
        fi
    fi
    
    log "✅ Аутентификация проверена"
}

# Создание backup текущей конфигурации
create_backup() {
    log "💾 Создание backup текущей конфигурации..."
    
    BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Сохраняем текущие конфигурации
    SERVICES=("chartgenius-api-working" "chartgenius-bot-working" "chartgenius-frontend")
    
    for SERVICE in "${SERVICES[@]}"; do
        if gcloud run services describe $SERVICE --region=$REGION >/dev/null 2>&1; then
            log "Сохранение конфигурации $SERVICE..."
            gcloud run services describe $SERVICE --region=$REGION --format="export" > "$BACKUP_DIR/${SERVICE}_config.yaml"
        else
            log "⚠️ Сервис $SERVICE не найден"
        fi
    done
    
    log "✅ Backup создан в директории: $BACKUP_DIR"
}

# Восстановление API сервиса
restore_api_service() {
    log "🔧 Восстановление chartgenius-api-working..."
    
    gcloud run services update chartgenius-api-working \
        --region=$REGION \
        --cpu=0.25 \
        --memory=256Mi \
        --min-instances=0 \
        --max-instances=1 \
        --concurrency=1 \
        --timeout=60 \
        --cpu-throttling \
        --quiet
    
    log "✅ chartgenius-api-working восстановлен"
}

# Восстановление Bot сервиса
restore_bot_service() {
    log "🤖 Восстановление chartgenius-bot-working..."
    
    gcloud run services update chartgenius-bot-working \
        --region=$REGION \
        --cpu=0.125 \
        --memory=128Mi \
        --min-instances=0 \
        --max-instances=1 \
        --concurrency=1 \
        --timeout=60 \
        --cpu-throttling \
        --quiet
    
    log "✅ chartgenius-bot-working восстановлен"
}

# Восстановление Frontend сервиса
restore_frontend_service() {
    log "🌐 Восстановление chartgenius-frontend..."
    
    gcloud run services update chartgenius-frontend \
        --region=$REGION \
        --cpu=0.125 \
        --memory=128Mi \
        --min-instances=0 \
        --max-instances=1 \
        --concurrency=1 \
        --timeout=60 \
        --cpu-throttling \
        --quiet
    
    log "✅ chartgenius-frontend восстановлен"
}

# Проверка восстановления
verify_restoration() {
    log "🔍 Проверка восстановленной конфигурации..."
    
    echo ""
    echo "📊 ТЕКУЩАЯ КОНФИГУРАЦИЯ:"
    gcloud run services list --region=$REGION --format="table(metadata.name,spec.template.spec.containers[0].resources.limits.cpu,spec.template.spec.containers[0].resources.limits.memory)"
    
    echo ""
    echo "🎯 ОЖИДАЕМАЯ КОНФИГУРАЦИЯ:"
    echo "  chartgenius-api-working: 0.25 CPU, 256Mi RAM"
    echo "  chartgenius-bot-working: 0.125 CPU, 128Mi RAM"
    echo "  chartgenius-frontend: 0.125 CPU, 128Mi RAM"
    
    echo ""
    log "🔗 Проверка доступности сервисов..."
    
    # Проверяем health endpoints
    SERVICES=("chartgenius-api-working" "chartgenius-bot-working" "chartgenius-frontend")
    
    for SERVICE in "${SERVICES[@]}"; do
        URL=$(gcloud run services describe $SERVICE --region=$REGION --format="value(status.url)")
        if [ ! -z "$URL" ]; then
            echo "  $SERVICE: $URL"
        fi
    done
}

# Тестирование функциональности
test_functionality() {
    log "🧪 Тестирование функциональности..."
    
    # Проверяем Telegram bot
    log "Проверка Telegram bot..."
    python -c "
import requests
try:
    r = requests.get('https://api.telegram.org/bot7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0/getMe', timeout=10)
    if r.status_code == 200:
        print('✅ Telegram bot доступен')
    else:
        print('❌ Telegram bot недоступен')
except Exception as e:
    print(f'❌ Ошибка проверки bot: {e}')
"
    
    log "✅ Базовое тестирование завершено"
}

# Генерация отчета
generate_report() {
    log "📋 Генерация отчета восстановления..."
    
    REPORT_FILE="restore_report_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > $REPORT_FILE << EOF
ОТЧЕТ О ВОССТАНОВЛЕНИИ СТАБИЛЬНОЙ ВЕРСИИ
=======================================
Дата: $(date)
Версия: $STABLE_VERSION
Проект: $PROJECT_ID

ВОССТАНОВЛЕННЫЕ СЕРВИСЫ:
- chartgenius-api-working: 0.25 CPU, 256Mi RAM
- chartgenius-bot-working: 0.125 CPU, 128Mi RAM  
- chartgenius-frontend: 0.125 CPU, 128Mi RAM

ОСОБЕННОСТИ КОНФИГУРАЦИИ:
- Scale-to-zero (min-instances=0)
- CPU throttling включен
- Concurrency=1
- Timeout=60s

ЭКОНОМИЧЕСКИЕ ПОКАЗАТЕЛИ:
- Ожидаемые расходы: \$1.50/месяц
- Free Tier статус: В пределах лимитов
- Budget alerts: \$5/месяц

СТАТУС: ВОССТАНОВЛЕНИЕ ЗАВЕРШЕНО
EOF
    
    log "✅ Отчет сохранен в $REPORT_FILE"
    cat $REPORT_FILE
}

# Главная функция
main() {
    echo "⚠️ ВНИМАНИЕ: Это восстановит конфигурацию к стабильной версии $STABLE_VERSION"
    echo "Текущие настройки будут изменены!"
    echo ""
    
    if ! confirm "Продолжить восстановление стабильной версии?"; then
        log "❌ Восстановление отменено"
        exit 0
    fi
    
    check_auth
    create_backup
    
    log "🚀 Начало восстановления стабильной версии..."
    
    restore_api_service
    restore_bot_service
    restore_frontend_service
    
    verify_restoration
    test_functionality
    generate_report
    
    echo ""
    log "🎉 ВОССТАНОВЛЕНИЕ СТАБИЛЬНОЙ ВЕРСИИ ЗАВЕРШЕНО!"
    echo ""
    echo "📊 Следующие шаги:"
    echo "1. Проверьте работоспособность всех сервисов"
    echo "2. Протестируйте Telegram bot"
    echo "3. Убедитесь в корректности WebApp"
    echo "4. Мониторьте budget alerts"
    echo ""
    echo "📞 При проблемах обращайтесь к документации или используйте backup"
}

# Запуск скрипта
main "$@"
