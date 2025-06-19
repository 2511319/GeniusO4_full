#!/bin/bash

# Скрипт для настройки Telegram бота
# Проект: chartgenius-444017

set -e

PROJECT_ID="chartgenius-444017"
REGION="us-central1"

echo "🤖 Настройка Telegram бота для ChartGenius"

# Проверяем наличие переменных окружения
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ Переменная TELEGRAM_BOT_TOKEN не установлена"
    echo "💡 Получите токен у @BotFather и установите:"
    echo "   export TELEGRAM_BOT_TOKEN=your_bot_token"
    exit 1
fi

# Получаем URL бота из Cloud Run
echo "📡 Получение URL бота из Cloud Run..."
BOT_URL=$(gcloud run services describe chartgenius-bot --region=$REGION --format="value(status.url)" 2>/dev/null)

if [ -z "$BOT_URL" ]; then
    echo "❌ Сервис chartgenius-bot не найден в Cloud Run"
    echo "💡 Сначала разверните приложение с помощью scripts/deploy_manual.sh"
    exit 1
fi

echo "🤖 Bot URL: $BOT_URL"

# Функция для выполнения API запросов к Telegram
telegram_api() {
    local method=$1
    local data=$2
    
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/$method" \
        -H "Content-Type: application/json" \
        -d "$data"
}

# Получаем информацию о боте
echo "📋 Получение информации о боте..."
bot_info=$(telegram_api "getMe" "{}")
bot_username=$(echo "$bot_info" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)

if [ -z "$bot_username" ]; then
    echo "❌ Не удалось получить информацию о боте. Проверьте токен."
    exit 1
fi

echo "✅ Бот найден: @$bot_username"

# Настройка webhook
echo "🔗 Настройка webhook..."
webhook_url="$BOT_URL/$TELEGRAM_BOT_TOKEN"
webhook_response=$(telegram_api "setWebhook" "{\"url\": \"$webhook_url\"}")

if echo "$webhook_response" | grep -q '"ok":true'; then
    echo "✅ Webhook настроен успешно: $webhook_url"
else
    echo "❌ Ошибка настройки webhook:"
    echo "$webhook_response"
    exit 1
fi

# Настройка команд бота
echo "⚙️ Настройка команд бота..."
commands_data='{
    "commands": [
        {
            "command": "start",
            "description": "Начать работу с ботом"
        },
        {
            "command": "help",
            "description": "Показать справку"
        },
        {
            "command": "dashboard",
            "description": "Открыть личный кабинет"
        }
    ]
}'

commands_response=$(telegram_api "setMyCommands" "$commands_data")

if echo "$commands_response" | grep -q '"ok":true'; then
    echo "✅ Команды бота настроены успешно"
else
    echo "❌ Ошибка настройки команд:"
    echo "$commands_response"
fi

# Настройка описания бота
echo "📝 Настройка описания бота..."
description="ChartGenius - профессиональная платформа для анализа криптовалют с использованием передовых технических индикаторов и алгоритмов прогнозирования."

description_response=$(telegram_api "setMyDescription" "{\"description\": \"$description\"}")

if echo "$description_response" | grep -q '"ok":true'; then
    echo "✅ Описание бота обновлено"
else
    echo "⚠️ Не удалось обновить описание бота"
fi

# Настройка краткого описания
short_description="Профессиональный анализ криптовалют с ИИ"
short_desc_response=$(telegram_api "setMyShortDescription" "{\"short_description\": \"$short_description\"}")

if echo "$short_desc_response" | grep -q '"ok":true'; then
    echo "✅ Краткое описание бота обновлено"
else
    echo "⚠️ Не удалось обновить краткое описание бота"
fi

# Проверка текущего webhook
echo "🔍 Проверка настроек webhook..."
webhook_info=$(telegram_api "getWebhookInfo" "{}")
echo "📋 Информация о webhook:"
echo "$webhook_info" | python3 -m json.tool 2>/dev/null || echo "$webhook_info"

echo ""
echo "🎉 Настройка Telegram бота завершена!"
echo ""
echo "📋 Сводка:"
echo "• Бот: @$bot_username"
echo "• Webhook: $webhook_url"
echo "• Команды: /start, /help, /dashboard"
echo ""
echo "📝 Следующие шаги:"
echo "1. Протестируйте бота, отправив /start"
echo "2. Проверьте логи Cloud Run при необходимости:"
echo "   gcloud run services logs read chartgenius-bot --region=$REGION"
echo ""
echo "🔧 Полезные команды для отладки:"
echo "• Просмотр webhook: curl -X POST \"https://api.telegram.org/bot\$TELEGRAM_BOT_TOKEN/getWebhookInfo\""
echo "• Удаление webhook: curl -X POST \"https://api.telegram.org/bot\$TELEGRAM_BOT_TOKEN/deleteWebhook\""
echo "• Получение обновлений: curl -X POST \"https://api.telegram.org/bot\$TELEGRAM_BOT_TOKEN/getUpdates\""
echo ""
