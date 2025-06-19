@echo off
REM Скрипт настройки Google Cloud Platform для ChartGenius (Windows)
REM Проект: chartgenius-444017

setlocal enabledelayedexpansion

set PROJECT_ID=chartgenius-444017
set REGION=us-central1

echo 🚀 Настройка Google Cloud Platform для проекта %PROJECT_ID%

REM Проверяем, что gcloud установлен
where gcloud >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ gcloud CLI не установлен. Установите Google Cloud SDK.
    pause
    exit /b 1
)

REM Устанавливаем проект по умолчанию
echo 📋 Устанавливаем проект %PROJECT_ID%...
gcloud config set project %PROJECT_ID%

REM Включаем необходимые API
echo 🔧 Включаем необходимые API...
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable monitoring.googleapis.com

echo ✅ API включены успешно

REM Создаем Firestore базу данных
echo 🗄️ Создаем Firestore базу данных...
gcloud firestore databases describe --region=%REGION% >nul 2>nul
if %errorlevel% neq 0 (
    gcloud firestore databases create --region=%REGION%
    echo ✅ Firestore база данных создана
) else (
    echo ℹ️ Firestore база данных уже существует
)

REM Создаем секреты
echo 🔐 Создаем секреты в Secret Manager...

REM Функция для создания секрета
call :create_secret "JWT_SECRET_KEY" "JWT secret key for authentication"
call :create_secret "TELEGRAM_BOT_TOKEN" "Telegram bot token"
call :create_secret "OPENAI_API_KEY" "OpenAI API key for analysis"
call :create_secret "CRYPTOCOMPARE_API_KEY" "CryptoCompare API key for market data"

REM Создаем сервисный аккаунт для GitHub Actions
echo 👤 Создаем сервисный аккаунт для CI/CD...
set SA_NAME=github-actions
set SA_EMAIL=%SA_NAME%@%PROJECT_ID%.iam.gserviceaccount.com

gcloud iam service-accounts describe %SA_EMAIL% >nul 2>nul
if %errorlevel% neq 0 (
    gcloud iam service-accounts create %SA_NAME% --display-name="GitHub Actions Service Account" --description="Service account for GitHub Actions CI/CD"
    echo ✅ Сервисный аккаунт создан
) else (
    echo ℹ️ Сервисный аккаунт уже существует
)

REM Назначаем роли сервисному аккаунту
echo 🔑 Назначаем роли сервисному аккаунту...
gcloud projects add-iam-policy-binding %PROJECT_ID% --member="serviceAccount:%SA_EMAIL%" --role="roles/run.developer"
gcloud projects add-iam-policy-binding %PROJECT_ID% --member="serviceAccount:%SA_EMAIL%" --role="roles/cloudbuild.builds.builder"
gcloud projects add-iam-policy-binding %PROJECT_ID% --member="serviceAccount:%SA_EMAIL%" --role="roles/secretmanager.secretAccessor"
gcloud projects add-iam-policy-binding %PROJECT_ID% --member="serviceAccount:%SA_EMAIL%" --role="roles/storage.admin"

echo ✅ Роли назначены

REM Создаем ключ для сервисного аккаунта
echo 🗝️ Создаем ключ для сервисного аккаунта...
if not exist "github-actions-key.json" (
    gcloud iam service-accounts keys create github-actions-key.json --iam-account=%SA_EMAIL%
    echo ✅ Ключ создан: github-actions-key.json
    echo ⚠️ Добавьте содержимое этого файла в GitHub Secrets как GCP_SA_KEY
) else (
    echo ℹ️ Ключ уже существует
)

echo.
echo 🎉 Настройка Google Cloud Platform завершена!
echo.
echo 📝 Следующие шаги:
echo 1. Обновите секреты в Secret Manager:
echo    - Запустите scripts\update_secrets.bat
echo.
echo 2. Добавьте в GitHub Secrets:
echo    - GCP_PROJECT_ID: %PROJECT_ID%
echo    - GCP_SA_KEY: содержимое файла github-actions-key.json
echo.
echo 3. Настройте Firestore коллекции:
echo    - python scripts\setup_firestore.py
echo.
echo 4. Запустите деплой: scripts\deploy_manual.bat
echo.

pause
goto :eof

:create_secret
set secret_name=%~1
set secret_description=%~2

gcloud secrets describe %secret_name% >nul 2>nul
if %errorlevel% neq 0 (
    echo 🔐 Создаем секрет %secret_name%...
    echo PLACEHOLDER_VALUE | gcloud secrets create %secret_name% --data-file=- --labels=project=chartgenius,environment=production
    echo ✅ Секрет %secret_name% создан ^(требуется обновление значения^)
) else (
    echo ℹ️ Секрет %secret_name% уже существует
)
goto :eof
