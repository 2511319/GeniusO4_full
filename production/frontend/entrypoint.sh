#!/bin/sh
# production/frontend/entrypoint.sh
# Скрипт для подстановки переменных окружения в nginx конфигурацию

set -e

echo "🚀 Запуск ChartGenius Frontend (Production)"
echo "📊 Версия: $(cat /app/VERSION 2>/dev/null || echo 'unknown')"
echo "🌍 Регион: ${GCP_REGION:-unknown}"

# Устанавливаем значения по умолчанию для переменных окружения
BACKEND_URL=${BACKEND_URL:-"https://chartgenius-api-169129692197.europe-west1.run.app"}
GCP_REGION=${GCP_REGION:-"europe-west1"}

echo "🔗 Backend URL: $BACKEND_URL"

# Создаем временный файл конфигурации nginx
NGINX_CONF="/etc/nginx/conf.d/default.conf"
NGINX_TEMPLATE="/etc/nginx/conf.d/default.conf.template"

# Если есть шаблон, используем его, иначе используем существующий файл как шаблон
if [ -f "$NGINX_TEMPLATE" ]; then
    echo "📝 Используем шаблон nginx конфигурации"
    cp "$NGINX_TEMPLATE" "$NGINX_CONF"
else
    echo "📝 Создаем шаблон из существующей конфигурации"
    cp "$NGINX_CONF" "$NGINX_TEMPLATE"
fi

# Подставляем переменные окружения в конфигурацию nginx
echo "🔧 Подстановка переменных окружения в nginx конфигурацию..."

# Используем envsubst для подстановки переменных
envsubst '${BACKEND_URL} ${GCP_REGION}' < "$NGINX_TEMPLATE" > "$NGINX_CONF"

# Проверяем корректность конфигурации nginx
echo "✅ Проверка конфигурации nginx..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Конфигурация nginx корректна"
else
    echo "❌ Ошибка в конфигурации nginx"
    exit 1
fi

# Создаем файл с информацией о сборке
cat > /usr/share/nginx/html/build-info.json << EOF
{
  "version": "$(cat /app/VERSION 2>/dev/null || echo 'unknown')",
  "buildTime": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "environment": "production",
  "region": "${GCP_REGION}",
  "backendUrl": "${BACKEND_URL}",
  "nginxVersion": "$(nginx -v 2>&1 | cut -d' ' -f3)"
}
EOF

echo "📋 Информация о сборке создана"

# Запускаем nginx
echo "🚀 Запуск nginx..."
exec nginx -g "daemon off;"
