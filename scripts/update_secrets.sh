#!/bin/bash

# Скрипт для обновления секретов в Google Secret Manager
# Проект: chartgenius-444017

set -e

PROJECT_ID="chartgenius-444017"

echo "🔐 Обновление секретов в Google Secret Manager для проекта $PROJECT_ID"

# Устанавливаем проект
gcloud config set project $PROJECT_ID

# Функция для безопасного обновления секрета
update_secret() {
    local secret_name=$1
    local secret_description=$2
    
    echo ""
    echo "🔑 Обновление секрета: $secret_name"
    echo "📝 Описание: $secret_description"
    echo "💡 Введите новое значение (ввод будет скрыт):"
    
    # Читаем секретное значение без отображения
    read -s secret_value
    
    if [ -z "$secret_value" ]; then
        echo "⚠️ Пустое значение, пропускаем $secret_name"
        return
    fi
    
    # Обновляем секрет
    echo "$secret_value" | gcloud secrets versions add $secret_name --data-file=-
    echo "✅ Секрет $secret_name обновлен"
}

# Функция для генерации JWT секрета
generate_jwt_secret() {
    echo ""
    echo "🎲 Генерация JWT секрета..."
    echo "Хотите сгенерировать случайный JWT секрет? (y/n)"
    read -r generate_jwt
    
    if [ "$generate_jwt" = "y" ] || [ "$generate_jwt" = "Y" ]; then
        # Генерируем случайный 64-символьный секрет
        jwt_secret=$(openssl rand -hex 32)
        echo "$jwt_secret" | gcloud secrets versions add JWT_SECRET_KEY --data-file=-
        echo "✅ JWT секрет сгенерирован и обновлен"
        echo "🔑 Сгенерированный секрет: $jwt_secret"
        echo "⚠️ Сохраните этот секрет в безопасном месте!"
    else
        update_secret "JWT_SECRET_KEY" "JWT secret key for authentication (минимум 32 символа)"
    fi
}

echo "Выберите действие:"
echo "1. Обновить все секреты"
echo "2. Обновить конкретный секрет"
echo "3. Сгенерировать новый JWT секрет"
echo "4. Показать текущие секреты"
read -r choice

case $choice in
    1)
        echo "🔄 Обновление всех секретов..."
        generate_jwt_secret
        update_secret "TELEGRAM_BOT_TOKEN" "Telegram bot token (получить у @BotFather)"
        update_secret "OPENAI_API_KEY" "OpenAI API key (sk-...)"
        update_secret "CRYPTOCOMPARE_API_KEY" "CryptoCompare API key (опционально)"
        ;;
    2)
        echo "Выберите секрет для обновления:"
        echo "1. JWT_SECRET_KEY"
        echo "2. TELEGRAM_BOT_TOKEN"
        echo "3. OPENAI_API_KEY"
        echo "4. CRYPTOCOMPARE_API_KEY"
        read -r secret_choice
        
        case $secret_choice in
            1) generate_jwt_secret ;;
            2) update_secret "TELEGRAM_BOT_TOKEN" "Telegram bot token" ;;
            3) update_secret "OPENAI_API_KEY" "OpenAI API key" ;;
            4) update_secret "CRYPTOCOMPARE_API_KEY" "CryptoCompare API key" ;;
            *) echo "❌ Неверный выбор" ;;
        esac
        ;;
    3)
        generate_jwt_secret
        ;;
    4)
        echo "📋 Текущие секреты:"
        gcloud secrets list --filter="labels.project=chartgenius"
        echo ""
        echo "🔍 Для просмотра версий секрета используйте:"
        echo "gcloud secrets versions list SECRET_NAME"
        ;;
    *)
        echo "❌ Неверный выбор"
        exit 1
        ;;
esac

echo ""
echo "✅ Операция завершена!"
echo ""
echo "📝 Полезные команды:"
echo "• Просмотр секретов: gcloud secrets list"
echo "• Просмотр версий: gcloud secrets versions list SECRET_NAME"
echo "• Получение значения: gcloud secrets versions access latest --secret=SECRET_NAME"
echo ""
