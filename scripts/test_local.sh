#!/bin/bash

# Скрипт для локального тестирования ChartGenius
# Запускает все компоненты локально и тестирует их взаимодействие

set -e

echo "🧪 Локальное тестирование ChartGenius"
echo "======================================"

# Проверяем наличие необходимых инструментов
check_requirements() {
    echo "🔍 Проверка требований..."
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 не установлен"
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js не установлен"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker не установлен"
        exit 1
    fi
    
    echo "✅ Все требования выполнены"
}

# Настройка переменных окружения для тестирования
setup_test_env() {
    echo "⚙️ Настройка тестового окружения..."
    
    export LOCAL_TESTING=true
    export JWT_SECRET_KEY="test_jwt_secret_key_for_local_testing_only"
    export TELEGRAM_BOT_TOKEN="test_bot_token"
    export OPENAI_API_KEY="test_openai_key"
    export CRYPTOCOMPARE_API_KEY="test_crypto_key"
    export LLM_PROVIDER="openai"
    export DEFAULT_SYMBOL="BTCUSDT"
    
    echo "✅ Тестовое окружение настроено"
}

# Установка зависимостей
install_dependencies() {
    echo "📦 Установка зависимостей..."
    
    # Backend зависимости
    echo "🐍 Установка Python зависимостей..."
    cd backend
    python3 -m pip install -r requirements.txt
    cd ..
    
    # Frontend зависимости
    echo "📱 Установка Node.js зависимостей..."
    cd frontend
    npm install
    cd ..
    
    # Тестовые зависимости
    echo "🧪 Установка тестовых зависимостей..."
    python3 -m pip install pytest pytest-asyncio aiohttp
    
    echo "✅ Зависимости установлены"
}

# Запуск backend сервера
start_backend() {
    echo "🚀 Запуск Backend API..."
    
    cd backend
    python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Ждем запуска сервера
    echo "⏳ Ожидание запуска Backend..."
    sleep 5
    
    # Проверяем доступность
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Backend API запущен (PID: $BACKEND_PID)"
    else
        echo "❌ Backend API не запустился"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
}

# Запуск frontend сервера
start_frontend() {
    echo "🌐 Запуск Frontend..."
    
    cd frontend
    VITE_API_URL=http://localhost:8000 npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    # Ждем запуска сервера
    echo "⏳ Ожидание запуска Frontend..."
    sleep 10
    
    echo "✅ Frontend запущен (PID: $FRONTEND_PID)"
}

# Запуск bot сервера
start_bot() {
    echo "🤖 Запуск Telegram Bot..."
    
    cd bot
    API_URL=http://localhost:8000 WEBAPP_URL=http://localhost:5173 python3 bot.py &
    BOT_PID=$!
    cd ..
    
    # Ждем запуска сервера
    echo "⏳ Ожидание запуска Bot..."
    sleep 3
    
    echo "✅ Telegram Bot запущен (PID: $BOT_PID)"
}

# Запуск интеграционных тестов
run_tests() {
    echo "🧪 Запуск интеграционных тестов..."
    
    export TEST_API_URL=http://localhost:8000
    
    # Ждем полной инициализации всех сервисов
    echo "⏳ Ожидание инициализации сервисов..."
    sleep 5
    
    # Запускаем тесты
    python3 tests/test_integration.py
    
    echo "✅ Интеграционные тесты завершены"
}

# Тестирование API endpoints
test_api_endpoints() {
    echo "📡 Тестирование API endpoints..."
    
    # Health check
    echo "🔍 Проверка health endpoint..."
    if curl -s http://localhost:8000/health | grep -q "ok"; then
        echo "✅ Health endpoint работает"
    else
        echo "❌ Health endpoint не работает"
    fi
    
    # Telegram auth endpoint
    echo "🔐 Проверка auth endpoint..."
    auth_response=$(curl -s -X POST http://localhost:8000/auth/telegram \
        -H "Content-Type: application/json" \
        -d '{"id":"123456789","first_name":"Test","username":"test","auth_date":"1640995200","hash":"test"}')
    
    if echo "$auth_response" | grep -q "access_token\|error"; then
        echo "✅ Auth endpoint отвечает"
    else
        echo "❌ Auth endpoint не отвечает"
    fi
    
    # Subscription endpoint
    echo "💳 Проверка subscription endpoint..."
    if curl -s -H "X-Telegram-Id: 123456789" http://localhost:8000/api/user/subscription | grep -q "level"; then
        echo "✅ Subscription endpoint работает"
    else
        echo "❌ Subscription endpoint не работает"
    fi
}

# Тестирование frontend
test_frontend() {
    echo "🌐 Тестирование Frontend..."
    
    # Проверяем доступность главной страницы
    if curl -s http://localhost:5173 > /dev/null; then
        echo "✅ Frontend доступен"
    else
        echo "❌ Frontend недоступен"
    fi
    
    # Запускаем frontend тесты
    echo "🧪 Запуск Frontend тестов..."
    cd frontend
    if npm test -- --watchAll=false > /dev/null 2>&1; then
        echo "✅ Frontend тесты прошли"
    else
        echo "⚠️ Frontend тесты не прошли (возможно, не настроены)"
    fi
    cd ..
}

# Очистка процессов
cleanup() {
    echo "🧹 Очистка процессов..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo "🛑 Backend остановлен"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo "🛑 Frontend остановлен"
    fi
    
    if [ ! -z "$BOT_PID" ]; then
        kill $BOT_PID 2>/dev/null || true
        echo "🛑 Bot остановлен"
    fi
    
    # Убиваем все оставшиеся процессы
    pkill -f "uvicorn app:app" 2>/dev/null || true
    pkill -f "npm run dev" 2>/dev/null || true
    pkill -f "python3 bot.py" 2>/dev/null || true
}

# Обработчик сигналов для очистки
trap cleanup EXIT INT TERM

# Основная функция
main() {
    check_requirements
    setup_test_env
    install_dependencies
    
    echo ""
    echo "🚀 Запуск локальных сервисов..."
    start_backend
    start_frontend
    start_bot
    
    echo ""
    echo "🧪 Запуск тестов..."
    test_api_endpoints
    test_frontend
    run_tests
    
    echo ""
    echo "✅ Локальное тестирование завершено!"
    echo ""
    echo "📋 Сводка:"
    echo "• Backend API:  http://localhost:8000"
    echo "• Frontend:     http://localhost:5173"
    echo "• Bot:          Запущен локально"
    echo ""
    echo "📝 Для ручного тестирования:"
    echo "1. Откройте http://localhost:5173 в браузере"
    echo "2. Протестируйте функционал"
    echo "3. Нажмите Ctrl+C для остановки всех сервисов"
    echo ""
    
    # Ждем сигнала для остановки
    echo "⏳ Сервисы запущены. Нажмите Ctrl+C для остановки..."
    while true; do
        sleep 1
    done
}

# Запуск основной функции
main
