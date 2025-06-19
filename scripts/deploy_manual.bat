@echo off
REM Скрипт для ручного развертывания ChartGenius в Google Cloud Run (Windows)
REM Проект: chartgenius-444017

setlocal enabledelayedexpansion

set PROJECT_ID=chartgenius-444017
set REGION=us-central1

REM Получаем короткий хеш коммита
for /f %%i in ('git rev-parse --short HEAD') do set COMMIT_SHA=%%i

echo 🚀 Ручное развертывание ChartGenius в Google Cloud Run
echo 📋 Проект: %PROJECT_ID%
echo 🌍 Регион: %REGION%
echo 🔖 Коммит: %COMMIT_SHA%

REM Устанавливаем проект
gcloud config set project %PROJECT_ID%

REM Проверяем, что секреты существуют
echo 🔐 Проверка секретов...
set required_secrets=JWT_SECRET_KEY TELEGRAM_BOT_TOKEN OPENAI_API_KEY

for %%s in (%required_secrets%) do (
    gcloud secrets describe %%s >nul 2>nul
    if !errorlevel! neq 0 (
        echo ❌ Секрет %%s не найден. Запустите scripts\setup_gcp.bat
        pause
        exit /b 1
    )
)
echo ✅ Все необходимые секреты найдены

REM Развертывание Backend API
echo.
echo 🔨 Сборка и развертывание chartgenius-api...
echo 📦 Сборка Docker образа...
gcloud builds submit --tag gcr.io/%PROJECT_ID%/chartgenius-api:%COMMIT_SHA% --dockerfile backend/Dockerfile .

echo 🚀 Развертывание в Cloud Run...
gcloud run deploy chartgenius-api ^
    --image gcr.io/%PROJECT_ID%/chartgenius-api:%COMMIT_SHA% ^
    --region %REGION% ^
    --platform managed ^
    --allow-unauthenticated ^
    --port 8000 ^
    --memory 1Gi ^
    --cpu 1 ^
    --max-instances 10 ^
    --set-secrets="JWT_SECRET_KEY=JWT_SECRET_KEY:latest,TELEGRAM_BOT_TOKEN=TELEGRAM_BOT_TOKEN:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest,CRYPTOCOMPARE_API_KEY=CRYPTOCOMPARE_API_KEY:latest" ^
    --set-env-vars="LLM_PROVIDER=openai,DEFAULT_SYMBOL=BTCUSDT,LOCAL_TESTING=false"

echo ✅ chartgenius-api развернут успешно

REM Получаем URL API для настройки других сервисов
for /f %%i in ('gcloud run services describe chartgenius-api --region=%REGION% --format="value(status.url)"') do set API_URL=%%i
echo 📡 API URL: %API_URL%

REM Развертывание Frontend
echo.
echo 🔨 Сборка Frontend с API URL...
gcloud builds submit ^
    --tag gcr.io/%PROJECT_ID%/chartgenius-frontend:%COMMIT_SHA% ^
    --dockerfile frontend/Dockerfile ^
    --build-arg VITE_API_URL=%API_URL% ^
    --build-arg VITE_TELEGRAM_BOT_USERNAME=Chart_Genius_bot ^
    .

gcloud run deploy chartgenius-frontend ^
    --image gcr.io/%PROJECT_ID%/chartgenius-frontend:%COMMIT_SHA% ^
    --region %REGION% ^
    --platform managed ^
    --allow-unauthenticated ^
    --port 80 ^
    --memory 512Mi ^
    --cpu 1 ^
    --max-instances 5

for /f %%i in ('gcloud run services describe chartgenius-frontend --region=%REGION% --format="value(status.url)"') do set FRONTEND_URL=%%i
echo 🌐 Frontend URL: %FRONTEND_URL%

REM Развертывание Telegram Bot
echo.
echo 🔨 Сборка и развертывание chartgenius-bot...
gcloud builds submit --tag gcr.io/%PROJECT_ID%/chartgenius-bot:%COMMIT_SHA% --dockerfile bot/Dockerfile .

gcloud run deploy chartgenius-bot ^
    --image gcr.io/%PROJECT_ID%/chartgenius-bot:%COMMIT_SHA% ^
    --region %REGION% ^
    --platform managed ^
    --allow-unauthenticated ^
    --port 8080 ^
    --memory 512Mi ^
    --cpu 1 ^
    --max-instances 5 ^
    --set-secrets="JWT_SECRET_KEY=JWT_SECRET_KEY:latest,TELEGRAM_BOT_TOKEN=TELEGRAM_BOT_TOKEN:latest" ^
    --set-env-vars="API_URL=%API_URL%,WEBAPP_URL=%FRONTEND_URL%"

for /f %%i in ('gcloud run services describe chartgenius-bot --region=%REGION% --format="value(status.url)"') do set BOT_URL=%%i
echo 🤖 Bot URL: %BOT_URL%

echo.
echo 🎉 Развертывание завершено!
echo.
echo 📋 Сводка развертывания:
echo • API:      %API_URL%
echo • Frontend: %FRONTEND_URL%
echo • Bot:      %BOT_URL%
echo.
echo 📝 Следующие шаги:
echo 1. Настройте webhook для Telegram бота:
echo    Запустите scripts\setup_telegram.bat
echo.
echo 2. Протестируйте приложение:
echo    • Откройте %FRONTEND_URL%
echo    • Отправьте /start боту в Telegram
echo.

pause
