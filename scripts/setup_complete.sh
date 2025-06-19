#!/bin/bash

# Полная настройка ChartGenius в Google Cloud Platform
# Проект: chartgenius-444017

set -e

PROJECT_ID="chartgenius-444017"
REGION="us-central1"

echo "🚀 Полная настройка ChartGenius в Google Cloud Platform"
echo "📋 Проект: $PROJECT_ID"
echo "🌍 Регион: $REGION"
echo ""

# Проверяем наличие необходимых инструментов
check_requirements() {
    echo "🔍 Проверка требований..."
    
    if ! command -v gcloud &> /dev/null; then
        echo "❌ gcloud CLI не установлен"
        echo "💡 Установите Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker не установлен"
        echo "💡 Установите Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 не установлен"
        exit 1
    fi
    
    echo "✅ Все требования выполнены"
}

# Интерактивный сбор секретов
collect_secrets() {
    echo ""
    echo "🔐 Сбор секретных данных..."
    echo "💡 Эти данные будут сохранены в Google Secret Manager"
    echo ""
    
    # JWT Secret
    echo "🔑 JWT Secret Key (оставьте пустым для автогенерации):"
    read -s jwt_secret
    if [ -z "$jwt_secret" ]; then
        jwt_secret=$(openssl rand -hex 32)
        echo "✅ JWT секрет сгенерирован автоматически"
    fi
    
    # Telegram Bot Token
    echo ""
    echo "🤖 Telegram Bot Token (получите у @BotFather):"
    read -s telegram_token
    if [ -z "$telegram_token" ]; then
        echo "❌ Telegram Bot Token обязателен"
        exit 1
    fi
    
    # OpenAI API Key
    echo ""
    echo "🧠 OpenAI API Key (sk-...):"
    read -s openai_key
    if [ -z "$openai_key" ]; then
        echo "❌ OpenAI API Key обязателен"
        exit 1
    fi
    
    # CryptoCompare API Key (опционально)
    echo ""
    echo "📈 CryptoCompare API Key (опционально, нажмите Enter для пропуска):"
    read -s crypto_key
    if [ -z "$crypto_key" ]; then
        crypto_key="not_required"
        echo "ℹ️ CryptoCompare API Key пропущен"
    fi
    
    echo ""
    echo "✅ Секреты собраны"
}

# Основная функция настройки
main() {
    check_requirements
    
    echo ""
    echo "Этот скрипт выполнит полную настройку ChartGenius:"
    echo "1. Настройка Google Cloud Platform"
    echo "2. Создание секретов"
    echo "3. Настройка Firestore"
    echo "4. Развертывание приложения"
    echo "5. Настройка Telegram бота"
    echo ""
    echo "Продолжить? (y/n)"
    read -r confirm
    
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "❌ Настройка отменена"
        exit 0
    fi
    
    collect_secrets
    
    # Шаг 1: Настройка GCP
    echo ""
    echo "📋 Шаг 1/5: Настройка Google Cloud Platform..."
    ./scripts/setup_gcp.sh
    
    # Шаг 2: Обновление секретов
    echo ""
    echo "🔐 Шаг 2/5: Создание секретов..."
    echo "$jwt_secret" | gcloud secrets versions add JWT_SECRET_KEY --data-file=-
    echo "$telegram_token" | gcloud secrets versions add TELEGRAM_BOT_TOKEN --data-file=-
    echo "$openai_key" | gcloud secrets versions add OPENAI_API_KEY --data-file=-
    echo "$crypto_key" | gcloud secrets versions add CRYPTOCOMPARE_API_KEY --data-file=-
    echo "✅ Секреты обновлены"
    
    # Шаг 3: Настройка Firestore
    echo ""
    echo "🗄️ Шаг 3/5: Настройка Firestore..."
    python3 scripts/setup_firestore.py
    
    # Шаг 4: Развертывание приложения
    echo ""
    echo "🚀 Шаг 4/5: Развертывание приложения..."
    ./scripts/deploy_manual.sh
    
    # Шаг 5: Настройка Telegram бота
    echo ""
    echo "🤖 Шаг 5/5: Настройка Telegram бота..."
    export TELEGRAM_BOT_TOKEN="$telegram_token"
    ./scripts/setup_telegram.sh
    
    # Финальная сводка
    echo ""
    echo "🎉 Полная настройка ChartGenius завершена!"
    echo ""
    
    # Получаем URL сервисов
    API_URL=$(gcloud run services describe chartgenius-api --region=$REGION --format="value(status.url)")
    FRONTEND_URL=$(gcloud run services describe chartgenius-frontend --region=$REGION --format="value(status.url)")
    BOT_URL=$(gcloud run services describe chartgenius-bot --region=$REGION --format="value(status.url)")
    
    echo "📋 Сводка развертывания:"
    echo "• 🌐 Frontend:  $FRONTEND_URL"
    echo "• 🔧 API:       $API_URL"
    echo "• 🤖 Bot:       $BOT_URL"
    echo ""
    echo "📝 Что делать дальше:"
    echo "1. Откройте $FRONTEND_URL в браузере"
    echo "2. Найдите вашего бота в Telegram и отправьте /start"
    echo "3. Протестируйте функционал анализа"
    echo "4. Настройте мониторинг в Google Cloud Console"
    echo ""
    echo "🔧 Полезные команды:"
    echo "• Логи API:      gcloud run services logs read chartgenius-api --region=$REGION"
    echo "• Логи Bot:      gcloud run services logs read chartgenius-bot --region=$REGION"
    echo "• Логи Frontend: gcloud run services logs read chartgenius-frontend --region=$REGION"
    echo ""
    echo "📚 Документация:"
    echo "• README.md - общая информация"
    echo "• DEPLOYMENT.md - детали развертывания"
    echo ""
}

# Делаем скрипты исполняемыми
chmod +x scripts/*.sh

# Запускаем основную функцию
main
