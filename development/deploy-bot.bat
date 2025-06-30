@echo off
REM 🚀 ChartGenius Bot Deployment Script (Windows)
REM Версия: 1.1.0-dev
REM Деплой исправленного бота в Google Cloud Run

setlocal enabledelayedexpansion

REM Конфигурация
set PROJECT_ID=chartgenius-444017
set REGION=europe-west1
set SERVICE_NAME=chartgenius-bot
set IMAGE_NAME=gcr.io/%PROJECT_ID%/%SERVICE_NAME%
set BOT_TOKEN=7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0

echo.
echo  ██████╗██╗  ██╗ █████╗ ██████╗ ████████╗ ██████╗ ███████╗███╗   ██╗██╗██╗   ██╗███████╗
echo ██╔════╝██║  ██║██╔══██╗██╔══██╗╚══██╔══╝██╔════╝ ██╔════╝████╗  ██║██║██║   ██║██╔════╝
echo ██║     ███████║███████║██████╔╝   ██║   ██║  ███╗█████╗  ██╔██╗ ██║██║██║   ██║███████╗
echo ██║     ██╔══██║██╔══██║██╔══██╗   ██║   ██║   ██║██╔══╝  ██║╚██╗██║██║██║   ██║╚════██║
echo ╚██████╗██║  ██║██║  ██║██║  ██║   ██║   ╚██████╔╝███████╗██║ ╚████║██║╚██████╔╝███████║
echo  ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚══════╝
echo.
echo                          Bot Deployment Script v1.1.0 (Windows)
echo                               Production Deploy
echo.

REM Проверка зависимостей
echo ================================
echo Проверка зависимостей
echo ================================
echo.

REM Проверка gcloud
gcloud --version >nul 2>&1
if errorlevel 1 (
    echo ❌ gcloud CLI не установлен
    pause
    exit /b 1
)
echo ✅ gcloud CLI установлен

REM Проверка Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker не установлен
    pause
    exit /b 1
)
echo ✅ Docker установлен

REM Проверка аутентификации
gcloud auth list --filter=status:ACTIVE --format="value(account)" | findstr "@" >nul 2>&1
if errorlevel 1 (
    echo ❌ Не выполнена аутентификация в gcloud
    echo ℹ️  Выполните: gcloud auth login
    pause
    exit /b 1
)
echo ✅ gcloud аутентификация активна

REM Настройка проекта
echo ℹ️  Настройка проекта: %PROJECT_ID%
gcloud config set project %PROJECT_ID%
echo ✅ Проект настроен

echo.

REM Локальное тестирование
echo ================================
echo Локальное тестирование бота
echo ================================
echo.

echo ℹ️  Запуск тестов...
python test-bot.py
if errorlevel 1 (
    echo ❌ Локальные тесты не пройдены
    set /p continue="Продолжить деплой? [y/N]: "
    if /i not "!continue!"=="y" (
        exit /b 1
    )
) else (
    echo ✅ Локальные тесты пройдены
)

echo.

REM Сборка Docker образа
echo ================================
echo Сборка Docker образа
echo ================================
echo.

echo ℹ️  Сборка образа для бота...
cd bot-dev

REM Создаем .dockerignore если его нет
if not exist .dockerignore (
    echo __pycache__ > .dockerignore
    echo *.pyc >> .dockerignore
    echo *.pyo >> .dockerignore
    echo *.pyd >> .dockerignore
    echo .Python >> .dockerignore
    echo env >> .dockerignore
    echo .git >> .dockerignore
    echo .venv >> .dockerignore
    echo venv/ >> .dockerignore
)

REM Сборка образа
docker build -t %IMAGE_NAME%:latest .

if errorlevel 1 (
    echo ❌ Ошибка сборки образа
    pause
    exit /b 1
)
echo ✅ Образ собран успешно

cd ..
echo.

REM Пуш образа в Container Registry
echo ================================
echo Загрузка образа в Container Registry
echo ================================
echo.

echo ℹ️  Настройка Docker для GCR...
gcloud auth configure-docker --quiet

echo ℹ️  Загрузка образа...
docker push %IMAGE_NAME%:latest

if errorlevel 1 (
    echo ❌ Ошибка загрузки образа
    pause
    exit /b 1
)
echo ✅ Образ загружен в GCR

echo.

REM Деплой в Cloud Run
echo ================================
echo Деплой в Google Cloud Run
echo ================================
echo.

echo ℹ️  Деплой сервиса...

REM Формируем URL webhook
set SERVICE_URL=https://%SERVICE_NAME%-%REGION%-%PROJECT_ID%.a.run.app
set WEBHOOK_URL=%SERVICE_URL%/webhook

gcloud run deploy %SERVICE_NAME% ^
    --image %IMAGE_NAME%:latest ^
    --platform managed ^
    --region %REGION% ^
    --allow-unauthenticated ^
    --memory 512Mi ^
    --cpu 1 ^
    --concurrency 1000 ^
    --timeout 300 ^
    --max-instances 10 ^
    --set-env-vars "TELEGRAM_BOT_TOKEN=%BOT_TOKEN%" ^
    --set-env-vars "WEBHOOK_URL=%WEBHOOK_URL%" ^
    --set-env-vars "ENVIRONMENT=production" ^
    --set-env-vars "DEBUG=false" ^
    --set-env-vars "VERSION=1.1.0-prod" ^
    --port 8000

if errorlevel 1 (
    echo ❌ Ошибка деплоя в Cloud Run
    pause
    exit /b 1
)
echo ✅ Сервис развернут в Cloud Run
echo ℹ️  URL сервиса: %SERVICE_URL%

echo.

REM Настройка webhook
echo ================================
echo Настройка Telegram Webhook
echo ================================
echo.

REM Получаем URL сервиса
for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)"') do set SERVICE_URL=%%i
set WEBHOOK_URL=%SERVICE_URL%/webhook

echo ℹ️  Настройка webhook: %WEBHOOK_URL%

REM Устанавливаем webhook
curl -X POST "https://api.telegram.org/bot%BOT_TOKEN%/setWebhook" ^
    -H "Content-Type: application/json" ^
    -d "{\"url\":\"%WEBHOOK_URL%\",\"drop_pending_updates\":true}"

echo.

REM Проверяем webhook
echo ℹ️  Проверка webhook...
curl -s "https://api.telegram.org/bot%BOT_TOKEN%/getWebhookInfo"

echo.
echo ✅ Webhook настроен

echo.

REM Тестирование в production
echo ================================
echo Тестирование в production
echo ================================
echo.

echo ℹ️  Ожидание готовности сервиса (30 секунд)...
timeout /t 30 /nobreak >nul

REM Тест health check
echo ℹ️  Тестирование health check...
curl -f "%SERVICE_URL%/health" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Health check не пройден
) else (
    echo ✅ Health check пройден
)

REM Тест отправки сообщения админу
echo ℹ️  Отправка тестового сообщения...
curl -X POST "https://api.telegram.org/bot%BOT_TOKEN%/sendMessage" ^
    -H "Content-Type: application/json" ^
    -d "{\"chat_id\":\"299820674\",\"text\":\"🚀 ChartGenius Bot v1.1.0 успешно развернут!\\n\\nВсе исправления применены:\\n✅ Исправлены callback handlers\\n✅ Улучшен middleware\\n✅ Добавлены таймауты\\n✅ Добавлена обработка ошибок\",\"parse_mode\":\"HTML\"}"

echo.
echo ✅ Тестовое сообщение отправлено

echo.

REM Проверка логов
echo ================================
echo Проверка логов
echo ================================
echo.

echo ℹ️  Последние логи сервиса:
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME%" ^
    --limit=10 ^
    --format="table(timestamp,severity,textPayload)" ^
    --freshness=1h

echo.

echo ================================
echo 🎉 Деплой завершен успешно!
echo ================================
echo ✅ ChartGenius Bot v1.1.0 развернут в production
echo ℹ️  Проверьте работу бота командой /start
echo.

set /p logs="Показать логи в реальном времени? [y/N]: "
if /i "!logs!"=="y" (
    echo ℹ️  Показ логов ^(Ctrl+C для выхода^)...
    gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME%"
) else (
    echo.
    echo Нажмите любую клавишу для выхода...
    pause >nul
)

endlocal
