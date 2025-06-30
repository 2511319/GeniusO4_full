@echo off
REM 🚀 ChartGenius Development Environment Startup Script (Windows)
REM Версия: 1.1.0-dev
REM Автоматический запуск всех сервисов для разработки

setlocal enabledelayedexpansion

echo.
echo  ██████╗██╗  ██╗ █████╗ ██████╗ ████████╗ ██████╗ ███████╗███╗   ██╗██╗██╗   ██╗███████╗
echo ██╔════╝██║  ██║██╔══██╗██╔══██╗╚══██╔══╝██╔════╝ ██╔════╝████╗  ██║██║██║   ██║██╔════╝
echo ██║     ███████║███████║██████╔╝   ██║   ██║  ███╗█████╗  ██╔██╗ ██║██║██║   ██║███████╗
echo ██║     ██╔══██║██╔══██║██╔══██╗   ██║   ██║   ██║██╔══╝  ██║╚██╗██║██║██║   ██║╚════██║
echo ╚██████╗██║  ██║██║  ██║██║  ██║   ██║   ╚██████╔╝███████╗██║ ╚████║██║╚██████╔╝███████║
echo  ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚══════╝
echo.
echo                          Development Environment v1.1.0-dev
echo                               Startup Script (Windows)
echo.

REM Проверка зависимостей
echo ================================
echo Проверка зависимостей
echo ================================
echo.

REM Проверка Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker не установлен. Установите Docker Desktop и попробуйте снова.
    pause
    exit /b 1
)
echo ✅ Docker установлен

REM Проверка Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова.
    pause
    exit /b 1
)
echo ✅ Docker Compose установлен

REM Проверка .env файла
if not exist ".env.development" (
    echo ⚠️  .env.development не найден. Создаю из примера...
    if exist ".env.development.example" (
        copy ".env.development.example" ".env.development" >nul
        echo ℹ️  Отредактируйте .env.development с вашими API ключами
    ) else (
        echo ❌ .env.development.example не найден
        pause
        exit /b 1
    )
)
echo ✅ .env.development найден

REM Проверка service account
if not exist "service-account.json" (
    echo ⚠️  service-account.json не найден
    echo ℹ️  Поместите ваш Google Cloud service account файл как service-account.json
    echo ℹ️  Или создайте пустой файл для тестирования: echo {} ^> service-account.json
) else (
    echo ✅ service-account.json найден
)

echo.

REM Остановка существующих контейнеров
echo ================================
echo Остановка существующих контейнеров
echo ================================
echo.

docker-compose -f docker-compose.dev.yml down --remove-orphans >nul 2>&1
docker-compose -f monitoring/docker-compose.monitoring.yml down --remove-orphans >nul 2>&1

echo ✅ Существующие контейнеры остановлены
echo.

REM Сборка образов
echo ================================
echo Сборка Docker образов
echo ================================
echo.

echo ℹ️  Сборка backend образа...
docker-compose -f docker-compose.dev.yml build backend-dev

echo ℹ️  Сборка frontend образа...
docker-compose -f docker-compose.dev.yml build frontend-dev

echo ℹ️  Сборка bot образа...
docker-compose -f docker-compose.dev.yml build bot-dev

echo ✅ Все образы собраны
echo.

REM Запуск основных сервисов
echo ================================
echo Запуск основных сервисов
echo ================================
echo.

echo ℹ️  Запуск Redis...
docker-compose -f docker-compose.dev.yml up -d redis-dev
timeout /t 5 /nobreak >nul

echo ℹ️  Запуск Celery Worker...
docker-compose -f docker-compose.dev.yml up -d celery-worker-dev
timeout /t 5 /nobreak >nul

echo ℹ️  Запуск Backend API...
docker-compose -f docker-compose.dev.yml up -d backend-dev
timeout /t 10 /nobreak >nul

echo ℹ️  Запуск Frontend...
docker-compose -f docker-compose.dev.yml up -d frontend-dev
timeout /t 5 /nobreak >nul

echo ℹ️  Запуск Telegram Bot...
docker-compose -f docker-compose.dev.yml up -d bot-dev
timeout /t 5 /nobreak >nul

echo ✅ Основные сервисы запущены
echo.

REM Запуск мониторинга
echo ================================
echo Запуск мониторинга (опционально)
echo ================================
echo.

set /p monitoring="Запустить мониторинг (Prometheus + Grafana)? [y/N]: "
if /i "!monitoring!"=="y" (
    echo ℹ️  Запуск мониторинга...
    docker-compose -f monitoring/docker-compose.monitoring.yml up -d
    timeout /t 10 /nobreak >nul
    echo ✅ Мониторинг запущен
) else (
    echo ℹ️  Мониторинг пропущен
)
echo.

REM Проверка здоровья сервисов
echo ================================
echo Проверка здоровья сервисов
echo ================================
echo.

echo ℹ️  Ожидание запуска сервисов (30 секунд)...
timeout /t 30 /nobreak >nul

echo ℹ️  Проверка Backend API...
curl -s http://localhost:8001/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Backend API недоступен
) else (
    echo ✅ Backend API работает
)

echo ℹ️  Проверка Frontend...
curl -s http://localhost:3001 >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Frontend недоступен
) else (
    echo ✅ Frontend работает
)

echo ℹ️  Проверка Redis...
docker exec chartgenius-redis-dev redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Redis недоступен
) else (
    echo ✅ Redis работает
)

echo ℹ️  Проверка Celery Worker...
docker-compose -f docker-compose.dev.yml ps celery-worker-dev | findstr "Up" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Celery Worker недоступен
) else (
    echo ✅ Celery Worker работает
)

echo.

REM Вывод информации о доступе
echo ================================
echo Информация о доступе к сервисам
echo ================================
echo.

echo 🌐 Web сервисы:
echo    Frontend:      http://localhost:3001
echo    Backend API:   http://localhost:8001
echo    Swagger UI:    http://localhost:8001/docs
echo    ReDoc:         http://localhost:8001/redoc
echo    Admin Panel:   http://localhost:3001/admin
echo.

echo 🔧 Инфраструктура:
echo    Redis:         localhost:6380
echo    Bot Webhook:   http://localhost:8002
echo.

docker-compose -f monitoring/docker-compose.monitoring.yml ps | findstr "Up" >nul 2>&1
if not errorlevel 1 (
    echo 📊 Мониторинг:
    echo    Prometheus:    http://localhost:9090
    echo    Grafana:       http://localhost:3000 ^(admin/admin^)
    echo    Redis UI:      http://localhost:8081
    echo.
)

echo 🔌 WebSocket:
echo    WebSocket:     ws://localhost:8001/ws/{user_id}
echo.

echo 📋 Полезные команды:
echo    Логи всех сервисов:    docker-compose -f docker-compose.dev.yml logs -f
echo    Логи backend:          docker-compose -f docker-compose.dev.yml logs -f backend-dev
echo    Остановка:             docker-compose -f docker-compose.dev.yml down
echo    Перезапуск:            start-dev.bat
echo.

echo 📚 Документация:
echo    README:        development/README.md
echo    API Docs:      development/docs/API.md
echo    Architecture:  development/docs/ARCHITECTURE.md
echo.

echo ================================
echo 🎉 ChartGenius Development Environment готов!
echo ================================
echo ✅ Все сервисы запущены и готовы к работе
echo ℹ️  Нажмите Ctrl+C для остановки или используйте: docker-compose -f docker-compose.dev.yml down
echo.

set /p logs="Показать логи в реальном времени? [y/N]: "
if /i "!logs!"=="y" (
    echo ℹ️  Показ логов ^(Ctrl+C для выхода^)...
    docker-compose -f docker-compose.dev.yml logs -f
) else (
    echo.
    echo Нажмите любую клавишу для выхода...
    pause >nul
)

endlocal
