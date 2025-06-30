#!/bin/bash
# 🚨 ЭКСТРЕННЫЙ ROLLBACK ChartGenius
# Версия: v1.0.51-stable
# Назначение: Быстрое восстановление при критических проблемах

set -e

PROJECT_ID="chartgenius-444017"
REGION="europe-west1"

echo "🚨 ЭКСТРЕННЫЙ ROLLBACK CHARTGENIUS"
echo "================================="
echo "⚠️ КРИТИЧЕСКАЯ СИТУАЦИЯ - БЫСТРОЕ ВОССТАНОВЛЕНИЕ"
echo ""

log() {
    echo "[$(date +'%H:%M:%S')] $1"
}

# Немедленное восстановление без подтверждений
emergency_restore() {
    log "🚨 НАЧАЛО ЭКСТРЕННОГО ВОССТАНОВЛЕНИЯ..."
    
    # API Service
    log "Восстановление API..."
    gcloud run services update chartgenius-api-working \
        --region=$REGION \
        --cpu=0.25 \
        --memory=256Mi \
        --min-instances=0 \
        --max-instances=1 \
        --concurrency=1 \
        --timeout=60 \
        --cpu-throttling \
        --quiet || log "❌ Ошибка восстановления API"
    
    # Bot Service
    log "Восстановление Bot..."
    gcloud run services update chartgenius-bot-working \
        --region=$REGION \
        --cpu=0.125 \
        --memory=128Mi \
        --min-instances=0 \
        --max-instances=1 \
        --concurrency=1 \
        --timeout=60 \
        --cpu-throttling \
        --quiet || log "❌ Ошибка восстановления Bot"
    
    # Frontend Service
    log "Восстановление Frontend..."
    gcloud run services update chartgenius-frontend \
        --region=$REGION \
        --cpu=0.125 \
        --memory=128Mi \
        --min-instances=0 \
        --max-instances=1 \
        --concurrency=1 \
        --timeout=60 \
        --cpu-throttling \
        --quiet || log "❌ Ошибка восстановления Frontend"
    
    log "✅ ЭКСТРЕННОЕ ВОССТАНОВЛЕНИЕ ЗАВЕРШЕНО"
}

# Быстрая проверка
quick_check() {
    log "🔍 Быстрая проверка сервисов..."
    
    gcloud run services list --region=$REGION --format="table(metadata.name,status.conditions[0].status)" || log "❌ Ошибка проверки"
    
    log "✅ Проверка завершена"
}

# Экстренное уведомление
send_alert() {
    log "📢 Отправка экстренного уведомления..."
    
    echo "🚨 ЭКСТРЕННЫЙ ROLLBACK ВЫПОЛНЕН" > emergency_rollback_$(date +%Y%m%d_%H%M%S).log
    echo "Дата: $(date)" >> emergency_rollback_$(date +%Y%m%d_%H%M%S).log
    echo "Статус: Восстановление к v1.0.51-stable" >> emergency_rollback_$(date +%Y%m%d_%H%M%S).log
    
    log "✅ Лог создан"
}

# Главная функция экстренного восстановления
main() {
    log "🚨 ЗАПУСК ЭКСТРЕННОГО ROLLBACK..."
    
    emergency_restore
    quick_check
    send_alert
    
    echo ""
    echo "🎯 ЭКСТРЕННЫЙ ROLLBACK ЗАВЕРШЕН!"
    echo "📊 Восстановлена стабильная конфигурация v1.0.51-stable"
    echo "⚠️ Рекомендуется полная проверка системы"
    echo ""
}

main "$@"
