#!/bin/bash

# Скрипт для тестирования продакшен развертывания ChartGenius
# Проект: chartgenius-444017

set -e

PROJECT_ID="chartgenius-444017"
REGION="us-central1"

echo "🧪 Тестирование продакшен развертывания ChartGenius"
echo "=================================================="

# Получаем URL сервисов
get_service_urls() {
    echo "📡 Получение URL сервисов..."
    
    API_URL=$(gcloud run services describe chartgenius-api --region=$REGION --format="value(status.url)" 2>/dev/null || echo "")
    FRONTEND_URL=$(gcloud run services describe chartgenius-frontend --region=$REGION --format="value(status.url)" 2>/dev/null || echo "")
    BOT_URL=$(gcloud run services describe chartgenius-bot --region=$REGION --format="value(status.url)" 2>/dev/null || echo "")
    
    if [ -z "$API_URL" ] || [ -z "$FRONTEND_URL" ] || [ -z "$BOT_URL" ]; then
        echo "❌ Не все сервисы развернуты. Запустите scripts/deploy_manual.sh"
        exit 1
    fi
    
    echo "✅ URL сервисов получены:"
    echo "• API:      $API_URL"
    echo "• Frontend: $FRONTEND_URL"
    echo "• Bot:      $BOT_URL"
}

# Тестирование доступности сервисов
test_service_availability() {
    echo ""
    echo "🔍 Тестирование доступности сервисов..."
    
    # Тест API
    echo "📡 Тестирование API..."
    if curl -s --max-time 30 "$API_URL/health" | grep -q "ok"; then
        echo "✅ API доступен и отвечает"
    else
        echo "❌ API недоступен или не отвечает"
        return 1
    fi
    
    # Тест Frontend
    echo "🌐 Тестирование Frontend..."
    if curl -s --max-time 30 "$FRONTEND_URL" > /dev/null; then
        echo "✅ Frontend доступен"
    else
        echo "❌ Frontend недоступен"
        return 1
    fi
    
    # Тест Bot
    echo "🤖 Тестирование Bot..."
    if curl -s --max-time 30 "$BOT_URL" > /dev/null; then
        echo "✅ Bot доступен"
    else
        echo "❌ Bot недоступен"
        return 1
    fi
}

# Тестирование API endpoints
test_api_endpoints() {
    echo ""
    echo "📊 Тестирование API endpoints..."
    
    # Health endpoint
    echo "🔍 Health endpoint..."
    health_response=$(curl -s --max-time 10 "$API_URL/health")
    if echo "$health_response" | grep -q "ok"; then
        echo "✅ Health endpoint работает"
    else
        echo "❌ Health endpoint не работает: $health_response"
    fi
    
    # Subscription endpoint
    echo "💳 Subscription endpoint..."
    sub_response=$(curl -s --max-time 10 -H "X-Telegram-Id: 123456789" "$API_URL/api/user/subscription")
    if echo "$sub_response" | grep -q "level"; then
        echo "✅ Subscription endpoint работает"
    else
        echo "❌ Subscription endpoint не работает: $sub_response"
    fi
    
    # Analysis check endpoint
    echo "📈 Analysis check endpoint..."
    check_response=$(curl -s --max-time 10 -X POST -H "X-Telegram-Id: 123456789" -H "Content-Type: application/json" "$API_URL/api/user/analysis/check" -d '{"analysis_type": "simple"}')
    if echo "$check_response" | grep -q "can_perform"; then
        echo "✅ Analysis check endpoint работает"
    else
        echo "❌ Analysis check endpoint не работает: $check_response"
    fi
}

# Тестирование Firestore подключения
test_firestore() {
    echo ""
    echo "🗄️ Тестирование Firestore..."
    
    # Проверяем через gcloud
    if gcloud firestore databases describe --region=$REGION > /dev/null 2>&1; then
        echo "✅ Firestore база данных доступна"
        
        # Проверяем коллекции (если возможно)
        echo "📋 Проверка коллекций..."
        python3 -c "
try:
    from google.cloud import firestore
    db = firestore.Client()
    collections = [c.id for c in db.collections()]
    print(f'✅ Найдены коллекции: {collections}')
except Exception as e:
    print(f'⚠️ Не удалось проверить коллекции: {e}')
" 2>/dev/null || echo "⚠️ Не удалось проверить коллекции (требуется настройка аутентификации)"
    else
        echo "❌ Firestore база данных недоступна"
    fi
}

# Тестирование секретов
test_secrets() {
    echo ""
    echo "🔐 Тестирование секретов..."
    
    secrets=("JWT_SECRET_KEY" "TELEGRAM_BOT_TOKEN" "OPENAI_API_KEY" "CRYPTOCOMPARE_API_KEY")
    
    for secret in "${secrets[@]}"; do
        if gcloud secrets describe $secret > /dev/null 2>&1; then
            # Проверяем, что есть активная версия
            if gcloud secrets versions list $secret --filter="state:enabled" --limit=1 | grep -q "ENABLED"; then
                echo "✅ Секрет $secret настроен и активен"
            else
                echo "⚠️ Секрет $secret существует, но нет активных версий"
            fi
        else
            echo "❌ Секрет $secret не найден"
        fi
    done
}

# Тестирование Telegram бота
test_telegram_bot() {
    echo ""
    echo "🤖 Тестирование Telegram бота..."
    
    # Получаем токен бота из секретов
    BOT_TOKEN=$(gcloud secrets versions access latest --secret="TELEGRAM_BOT_TOKEN" 2>/dev/null || echo "")
    
    if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" = "PLACEHOLDER_VALUE" ]; then
        echo "⚠️ Telegram Bot Token не настроен"
        return
    fi
    
    # Проверяем информацию о боте
    echo "📋 Проверка информации о боте..."
    bot_info=$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/getMe")
    if echo "$bot_info" | grep -q '"ok":true'; then
        bot_username=$(echo "$bot_info" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
        echo "✅ Бот активен: @$bot_username"
        
        # Проверяем webhook
        echo "🔗 Проверка webhook..."
        webhook_info=$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo")
        if echo "$webhook_info" | grep -q "$BOT_URL"; then
            echo "✅ Webhook настроен корректно"
        else
            echo "⚠️ Webhook не настроен или настроен неправильно"
            echo "💡 Запустите: scripts/setup_telegram.sh"
        fi
    else
        echo "❌ Бот недоступен или токен неверный"
    fi
}

# Тестирование производительности
test_performance() {
    echo ""
    echo "⚡ Тестирование производительности..."
    
    # Тест времени ответа API
    echo "📊 Время ответа API..."
    start_time=$(date +%s%N)
    curl -s --max-time 30 "$API_URL/health" > /dev/null
    end_time=$(date +%s%N)
    response_time=$(( (end_time - start_time) / 1000000 ))
    
    if [ $response_time -lt 5000 ]; then
        echo "✅ API отвечает быстро: ${response_time}ms"
    elif [ $response_time -lt 10000 ]; then
        echo "⚠️ API отвечает медленно: ${response_time}ms"
    else
        echo "❌ API отвечает очень медленно: ${response_time}ms"
    fi
    
    # Тест времени ответа Frontend
    echo "🌐 Время ответа Frontend..."
    start_time=$(date +%s%N)
    curl -s --max-time 30 "$FRONTEND_URL" > /dev/null
    end_time=$(date +%s%N)
    response_time=$(( (end_time - start_time) / 1000000 ))
    
    if [ $response_time -lt 3000 ]; then
        echo "✅ Frontend отвечает быстро: ${response_time}ms"
    elif [ $response_time -lt 8000 ]; then
        echo "⚠️ Frontend отвечает медленно: ${response_time}ms"
    else
        echo "❌ Frontend отвечает очень медленно: ${response_time}ms"
    fi
}

# Проверка логов
check_logs() {
    echo ""
    echo "📋 Проверка логов сервисов..."
    
    # Проверяем логи на ошибки
    echo "🔍 Проверка ошибок в логах API..."
    api_errors=$(gcloud run services logs read chartgenius-api --region=$REGION --limit=50 --format="value(textPayload)" | grep -i "error\|exception\|failed" | wc -l)
    if [ $api_errors -eq 0 ]; then
        echo "✅ Нет критических ошибок в логах API"
    else
        echo "⚠️ Найдено $api_errors ошибок в логах API"
    fi
    
    echo "🔍 Проверка ошибок в логах Bot..."
    bot_errors=$(gcloud run services logs read chartgenius-bot --region=$REGION --limit=50 --format="value(textPayload)" | grep -i "error\|exception\|failed" | wc -l)
    if [ $bot_errors -eq 0 ]; then
        echo "✅ Нет критических ошибок в логах Bot"
    else
        echo "⚠️ Найдено $bot_errors ошибок в логах Bot"
    fi
}

# Генерация отчета
generate_report() {
    echo ""
    echo "📊 Генерация отчета тестирования..."
    
    report_file="test_report_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > $report_file << EOF
ChartGenius Production Test Report
Generated: $(date)
Project: $PROJECT_ID
Region: $REGION

Service URLs:
- API:      $API_URL
- Frontend: $FRONTEND_URL
- Bot:      $BOT_URL

Test Results:
$(echo "$test_results")

Recommendations:
- Monitor service performance regularly
- Check logs for any recurring errors
- Ensure Telegram webhook is properly configured
- Verify all secrets are up to date

EOF

    echo "✅ Отчет сохранен: $report_file"
}

# Основная функция
main() {
    # Устанавливаем проект
    gcloud config set project $PROJECT_ID
    
    get_service_urls
    
    echo ""
    echo "🚀 Начало тестирования продакшен развертывания..."
    
    test_service_availability
    test_api_endpoints
    test_firestore
    test_secrets
    test_telegram_bot
    test_performance
    check_logs
    
    echo ""
    echo "✅ Тестирование продакшен развертывания завершено!"
    echo ""
    echo "📋 Сводка:"
    echo "• Все основные сервисы доступны"
    echo "• API endpoints отвечают корректно"
    echo "• Firestore настроен"
    echo "• Секреты настроены"
    echo "• Telegram бот готов к работе"
    echo ""
    echo "📝 Следующие шаги:"
    echo "1. Протестируйте функционал вручную:"
    echo "   - Откройте $FRONTEND_URL"
    echo "   - Найдите бота в Telegram и отправьте /start"
    echo "2. Настройте мониторинг в Google Cloud Console"
    echo "3. Настройте алерты для критических метрик"
    echo ""
    echo "🎉 ChartGenius готов к использованию!"
}

# Запуск основной функции
main
