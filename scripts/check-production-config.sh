#!/bin/bash
# scripts/check-production-config.sh
# Скрипт проверки готовности конфигурации к продакшену

set -e

echo "🔍 ПРОВЕРКА ГОТОВНОСТИ CHARTGENIUS К ПРОДАКШЕНУ"
echo "================================================"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Функции для вывода
error() {
    echo -e "${RED}❌ ОШИБКА: $1${NC}"
    ((ERRORS++))
}

warning() {
    echo -e "${YELLOW}⚠️  ПРЕДУПРЕЖДЕНИЕ: $1${NC}"
    ((WARNINGS++))
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 1. Проверка версий
echo -e "\n${BLUE}📊 ПРОВЕРКА ВЕРСИЙ${NC}"
echo "==================="

PROD_VERSION=$(cat production/VERSION 2>/dev/null || echo "НЕ НАЙДЕН")
FRONTEND_VERSION=$(grep '"version"' frontend/package.json | cut -d'"' -f4 2>/dev/null || echo "НЕ НАЙДЕН")

if [ -f "production/frontend/src/config.js" ]; then
    CONFIG_VERSION=$(grep 'APP_VERSION' production/frontend/src/config.js | cut -d"'" -f2 2>/dev/null || echo "НЕ НАЙДЕН")
else
    CONFIG_VERSION="ФАЙЛ НЕ НАЙДЕН"
fi

if [ -f "frontend/src/config.js" ]; then
    DEV_CONFIG_VERSION=$(grep 'APP_VERSION' frontend/src/config.js | cut -d"'" -f2 2>/dev/null || echo "НЕ НАЙДЕН")
else
    DEV_CONFIG_VERSION="ФАЙЛ НЕ НАЙДЕН"
fi

echo "Production VERSION: $PROD_VERSION"
echo "Frontend package.json: $FRONTEND_VERSION"
echo "Production config.js: $CONFIG_VERSION"
echo "Development config.js: $DEV_CONFIG_VERSION"

if [ "$PROD_VERSION" = "$FRONTEND_VERSION" ] && [ "$PROD_VERSION" = "$CONFIG_VERSION" ]; then
    success "Версии синхронизированы"
else
    error "Версии не синхронизированы между компонентами"
fi

# 2. Проверка API URL
echo -e "\n${BLUE}🔗 ПРОВЕРКА API URL${NC}"
echo "==================="

# Проверка на localhost в продакшн файлах
if grep -r "localhost\|127\.0\.0\.1" production/ 2>/dev/null; then
    error "Найдены localhost/127.0.0.1 в продакшн файлах"
else
    success "localhost не найден в продакшн файлах"
fi

# Проверка соответствия API URL в продакшн файлах
NGINX_API_URL=$(grep -o 'https://[^;]*\.run\.app' production/frontend/nginx.conf 2>/dev/null || echo "НЕ НАЙДЕН")
DOCKERFILE_API_URL=$(grep -o 'https://[^"]*\.run\.app' production/frontend/Dockerfile 2>/dev/null || echo "НЕ НАЙДЕН")

if [ -f "production/frontend/src/config.js" ]; then
    CONFIG_API_URL=$(grep -o 'https://[^"]*\.run\.app' production/frontend/src/config.js 2>/dev/null || echo "НЕ НАЙДЕН")
else
    CONFIG_API_URL="ФАЙЛ НЕ НАЙДЕН"
fi

echo "Nginx API URL: $NGINX_API_URL"
echo "Dockerfile API URL: $DOCKERFILE_API_URL"
echo "Config API URL: $CONFIG_API_URL"

if [ "$NGINX_API_URL" = "$DOCKERFILE_API_URL" ] && [ "$NGINX_API_URL" = "$CONFIG_API_URL" ]; then
    success "API URL синхронизированы в продакшн файлах"
else
    error "API URL не синхронизированы между продакшн файлами"
fi

# 3. Проверка секретов
echo -e "\n${BLUE}🔐 ПРОВЕРКА СЕКРЕТОВ${NC}"
echo "==================="

# Проверка на реальные токены в коде
if grep -r "sk-" . --exclude-dir=node_modules --exclude-dir=.git 2>/dev/null | grep -v "your-" | grep -v "example" | grep -v ".md"; then
    error "Найдены возможные реальные API ключи в коде"
else
    success "Реальные API ключи не найдены в коде"
fi

# Проверка Telegram токена в setup-secrets.ps1
if grep -q "7279183061:" production/setup-secrets.ps1 2>/dev/null; then
    error "Найден реальный Telegram токен в setup-secrets.ps1"
else
    success "Реальный Telegram токен не найден в скриптах"
fi

# 4. Проверка режимов отладки
echo -e "\n${BLUE}🐛 ПРОВЕРКА РЕЖИМОВ ОТЛАДКИ${NC}"
echo "============================="

# Проверка DEBUG в продакшн конфигурации
if [ -f "production/backend/config/production.py" ]; then
    if grep -q "DEBUG = False" production/backend/config/production.py; then
        success "DEBUG отключен в продакшн backend"
    else
        error "DEBUG не отключен в продакшн backend"
    fi
fi

if [ -f "production/frontend/src/config.js" ]; then
    if grep -q "DEBUG = false" production/frontend/src/config.js; then
        success "DEBUG отключен в продакшн frontend"
    else
        warning "DEBUG не отключен в продакшн frontend"
    fi
fi

# Проверка console.log в продакшн
if grep -r "console\.log" production/ 2>/dev/null; then
    warning "Найдены console.log в продакшн файлах"
else
    success "console.log не найдены в продакшн файлах"
fi

# 5. Проверка Docker файлов
echo -e "\n${BLUE}🐳 ПРОВЕРКА DOCKER КОНФИГУРАЦИИ${NC}"
echo "================================="

DOCKER_FILES=("production/backend/Dockerfile" "production/frontend/Dockerfile" "production/bot/Dockerfile")

for dockerfile in "${DOCKER_FILES[@]}"; do
    if [ -f "$dockerfile" ]; then
        success "Найден $dockerfile"
        
        # Проверка multi-stage build
        if grep -q "FROM.*AS" "$dockerfile"; then
            success "  Multi-stage build используется"
        else
            warning "  Multi-stage build не используется в $dockerfile"
        fi
        
        # Проверка health check
        if grep -q "HEALTHCHECK" "$dockerfile"; then
            success "  Health check настроен"
        else
            warning "  Health check не настроен в $dockerfile"
        fi
    else
        error "Не найден $dockerfile"
    fi
done

# 6. Проверка структуры проекта
echo -e "\n${BLUE}📁 ПРОВЕРКА СТРУКТУРЫ ПРОЕКТА${NC}"
echo "=============================="

REQUIRED_DIRS=("production" "backend" "frontend" "bot")
REQUIRED_FILES=("production/VERSION" "production/deploy-production.sh" "production/setup-secrets.sh")

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        success "Директория $dir существует"
    else
        error "Директория $dir не найдена"
    fi
done

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        success "Файл $file существует"
    else
        error "Файл $file не найден"
    fi
done

# 7. Итоговый отчет
echo -e "\n${BLUE}📋 ИТОГОВЫЙ ОТЧЕТ${NC}"
echo "=================="

echo "Найдено ошибок: $ERRORS"
echo "Найдено предупреждений: $WARNINGS"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ОТЛИЧНО! Проект полностью готов к продакшену${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "\n${YELLOW}⚠️  Проект готов к продакшену с незначительными замечаниями${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Проект НЕ готов к продакшену. Необходимо исправить ошибки${NC}"
    exit 1
fi
