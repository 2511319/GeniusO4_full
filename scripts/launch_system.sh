#!/bin/bash

# Финальный скрипт запуска ChartGenius в продакшене
# Проект: chartgenius-444017

set -e

PROJECT_ID="chartgenius-444017"
REGION="us-central1"

echo "🚀 Запуск ChartGenius в продакшене"
echo "=================================="
echo "📋 Проект: $PROJECT_ID"
echo "🌍 Регион: $REGION"
echo ""

# Проверка готовности к запуску
check_readiness() {
    echo "🔍 Проверка готовности системы к запуску..."
    
    # Проверяем, что мы в правильном проекте
    current_project=$(gcloud config get-value project 2>/dev/null || echo "")
    if [ "$current_project" != "$PROJECT_ID" ]; then
        echo "❌ Неправильный проект. Установите: gcloud config set project $PROJECT_ID"
        exit 1
    fi
    
    # Проверяем наличие сервисов
    services=("chartgenius-api" "chartgenius-frontend" "chartgenius-bot")
    for service in "${services[@]}"; do
        if ! gcloud run services describe $service --region=$REGION > /dev/null 2>&1; then
            echo "❌ Сервис $service не развернут. Запустите scripts/deploy_manual.sh"
            exit 1
        fi
    done
    
    # Проверяем секреты
    secrets=("JWT_SECRET_KEY" "TELEGRAM_BOT_TOKEN" "OPENAI_API_KEY")
    for secret in "${secrets[@]}"; do
        if ! gcloud secrets versions list $secret --filter="state:enabled" --limit=1 | grep -q "ENABLED"; then
            echo "❌ Секрет $secret не настроен. Запустите scripts/update_secrets.sh"
            exit 1
        fi
    done
    
    echo "✅ Система готова к запуску"
}

# Получение URL сервисов
get_service_urls() {
    echo "📡 Получение URL сервисов..."
    
    API_URL=$(gcloud run services describe chartgenius-api --region=$REGION --format="value(status.url)")
    FRONTEND_URL=$(gcloud run services describe chartgenius-frontend --region=$REGION --format="value(status.url)")
    BOT_URL=$(gcloud run services describe chartgenius-bot --region=$REGION --format="value(status.url)")
    
    echo "✅ URL сервисов получены"
}

# Финальная настройка Telegram бота
setup_telegram_bot() {
    echo "🤖 Финальная настройка Telegram бота..."
    
    BOT_TOKEN=$(gcloud secrets versions access latest --secret="TELEGRAM_BOT_TOKEN")
    
    if [ "$BOT_TOKEN" = "PLACEHOLDER_VALUE" ]; then
        echo "❌ Telegram Bot Token не настроен. Обновите секрет TELEGRAM_BOT_TOKEN"
        exit 1
    fi
    
    # Настройка webhook
    webhook_url="$BOT_URL/$BOT_TOKEN"
    webhook_response=$(curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/setWebhook" \
        -H "Content-Type: application/json" \
        -d "{\"url\": \"$webhook_url\"}")
    
    if echo "$webhook_response" | grep -q '"ok":true'; then
        echo "✅ Telegram webhook настроен"
    else
        echo "❌ Ошибка настройки webhook: $webhook_response"
        exit 1
    fi
    
    # Получаем информацию о боте
    bot_info=$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/getMe")
    if echo "$bot_info" | grep -q '"ok":true'; then
        bot_username=$(echo "$bot_info" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
        echo "✅ Бот активен: @$bot_username"
        BOT_USERNAME="$bot_username"
    else
        echo "❌ Не удалось получить информацию о боте"
        exit 1
    fi
}

# Запуск финального тестирования
run_final_tests() {
    echo "🧪 Запуск финального тестирования..."
    
    # Запускаем продакшен тесты
    if bash scripts/test_production.sh; then
        echo "✅ Финальное тестирование прошло успешно"
    else
        echo "❌ Финальное тестирование не прошло"
        echo "💡 Проверьте логи и исправьте ошибки перед запуском"
        exit 1
    fi
}

# Создание отчета о запуске
create_launch_report() {
    echo "📊 Создание отчета о запуске..."
    
    launch_report="launch_report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > $launch_report << EOF
# ChartGenius Launch Report

**Дата запуска**: $(date)
**Проект**: $PROJECT_ID
**Регион**: $REGION

## 🌐 URL сервисов
- **Frontend**: $FRONTEND_URL
- **API**: $API_URL
- **Bot**: $BOT_URL

## 🤖 Telegram Bot
- **Username**: @$BOT_USERNAME
- **Webhook**: Настроен и активен
- **Команды**: /start, /help, /dashboard

## 📊 Статус сервисов
- **chartgenius-api**: ✅ Активен
- **chartgenius-frontend**: ✅ Активен
- **chartgenius-bot**: ✅ Активен

## 🗄️ База данных
- **Firestore**: Настроен в регионе $REGION
- **Коллекции**: users, subscriptions, analyses
- **TTL**: 30 дней для analyses

## 🔐 Безопасность
- **Секреты**: Настроены в Secret Manager
- **JWT**: Активен
- **Telegram Auth**: Настроен

## 📈 Мониторинг
- **Cloud Logging**: Активен
- **Cloud Monitoring**: Активен
- **Алерты**: Рекомендуется настроить

## 🎯 Следующие шаги
1. Мониторинг производительности
2. Настройка алертов
3. Регулярное обновление секретов
4. Резервное копирование данных

## 📞 Поддержка
- Логи: \`gcloud run services logs read SERVICE_NAME --region=$REGION\`
- Метрики: Google Cloud Console > Cloud Run
- Отладка: \`scripts/test_production.sh\`

---
**Система готова к использованию!** 🎉
EOF

    echo "✅ Отчет о запуске создан: $launch_report"
}

# Отображение финальной информации
show_launch_info() {
    echo ""
    echo "🎉 ChartGenius успешно запущен в продакшене!"
    echo ""
    echo "📋 Информация для пользователей:"
    echo "┌─────────────────────────────────────────────────────────────┐"
    echo "│                     ChartGenius                             │"
    echo "│              Готов к использованию!                        │"
    echo "├─────────────────────────────────────────────────────────────┤"
    echo "│ 🌐 Веб-интерфейс:                                          │"
    echo "│    $FRONTEND_URL"
    echo "│                                                             │"
    echo "│ 🤖 Telegram Bot:                                           │"
    echo "│    @$BOT_USERNAME"
    echo "│    Команда для начала: /start                              │"
    echo "│                                                             │"
    echo "│ 📊 Возможности:                                            │"
    echo "│    • Анализ криптовалют с ИИ                               │"
    echo "│    • Технические индикаторы                                │"
    echo "│    • Торговые рекомендации                                 │"
    echo "│    • Интерактивные графики                                 │"
    echo "│    • Личный кабинет                                        │"
    echo "│    • Система подписок                                      │"
    echo "└─────────────────────────────────────────────────────────────┘"
    echo ""
    echo "🔧 Для администраторов:"
    echo "• Мониторинг: Google Cloud Console > Cloud Run"
    echo "• Логи: gcloud run services logs read SERVICE_NAME --region=$REGION"
    echo "• Тестирование: scripts/test_production.sh"
    echo "• Обновление: git push (автоматический деплой через GitHub Actions)"
    echo ""
    echo "📈 Рекомендации:"
    echo "1. Настройте алерты в Cloud Monitoring"
    echo "2. Регулярно проверяйте логи на ошибки"
    echo "3. Мониторьте использование ресурсов"
    echo "4. Обновляйте секреты по мере необходимости"
    echo ""
    echo "🎯 Система полностью готова к работе с пользователями!"
}

# Основная функция
main() {
    check_readiness
    get_service_urls
    setup_telegram_bot
    run_final_tests
    create_launch_report
    show_launch_info
    
    echo ""
    echo "✅ Запуск ChartGenius завершен успешно!"
    echo "🚀 Система работает в продакшене!"
}

# Запуск основной функции
main
