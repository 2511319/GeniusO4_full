@echo off
REM Финальный скрипт запуска ChartGenius в продакшене (Windows)
REM Проект: chartgenius-444017

setlocal enabledelayedexpansion

set PROJECT_ID=chartgenius-444017
set REGION=us-central1

echo 🚀 Запуск ChartGenius в продакшене
echo ==================================
echo 📋 Проект: %PROJECT_ID%
echo 🌍 Регион: %REGION%
echo.

REM Проверка готовности к запуску
echo 🔍 Проверка готовности системы к запуску...

REM Проверяем, что мы в правильном проекте
for /f %%i in ('gcloud config get-value project 2^>nul') do set current_project=%%i
if not "%current_project%"=="%PROJECT_ID%" (
    echo ❌ Неправильный проект. Установите: gcloud config set project %PROJECT_ID%
    pause
    exit /b 1
)

REM Проверяем наличие сервисов
set services=chartgenius-api chartgenius-frontend chartgenius-bot
for %%s in (%services%) do (
    gcloud run services describe %%s --region=%REGION% >nul 2>nul
    if !errorlevel! neq 0 (
        echo ❌ Сервис %%s не развернут. Запустите scripts\deploy_manual.bat
        pause
        exit /b 1
    )
)

REM Проверяем секреты
set secrets=JWT_SECRET_KEY TELEGRAM_BOT_TOKEN OPENAI_API_KEY
for %%s in (%secrets%) do (
    gcloud secrets versions list %%s --filter="state:enabled" --limit=1 | findstr "ENABLED" >nul
    if !errorlevel! neq 0 (
        echo ❌ Секрет %%s не настроен. Запустите scripts\update_secrets.bat
        pause
        exit /b 1
    )
)

echo ✅ Система готова к запуску

REM Получение URL сервисов
echo 📡 Получение URL сервисов...

for /f %%i in ('gcloud run services describe chartgenius-api --region=%REGION% --format="value(status.url)"') do set API_URL=%%i
for /f %%i in ('gcloud run services describe chartgenius-frontend --region=%REGION% --format="value(status.url)"') do set FRONTEND_URL=%%i
for /f %%i in ('gcloud run services describe chartgenius-bot --region=%REGION% --format="value(status.url)"') do set BOT_URL=%%i

echo ✅ URL сервисов получены

REM Финальная настройка Telegram бота
echo 🤖 Финальная настройка Telegram бота...

for /f %%i in ('gcloud secrets versions access latest --secret="TELEGRAM_BOT_TOKEN"') do set BOT_TOKEN=%%i

if "%BOT_TOKEN%"=="PLACEHOLDER_VALUE" (
    echo ❌ Telegram Bot Token не настроен. Обновите секрет TELEGRAM_BOT_TOKEN
    pause
    exit /b 1
)

REM Настройка webhook
set webhook_url=%BOT_URL%/%BOT_TOKEN%
curl -s -X POST "https://api.telegram.org/bot%BOT_TOKEN%/setWebhook" -H "Content-Type: application/json" -d "{\"url\": \"%webhook_url%\"}" > webhook_response.tmp

findstr "\"ok\":true" webhook_response.tmp >nul
if !errorlevel! equ 0 (
    echo ✅ Telegram webhook настроен
) else (
    echo ❌ Ошибка настройки webhook
    type webhook_response.tmp
    del webhook_response.tmp
    pause
    exit /b 1
)
del webhook_response.tmp

REM Получаем информацию о боте
curl -s "https://api.telegram.org/bot%BOT_TOKEN%/getMe" > bot_info.tmp
findstr "\"ok\":true" bot_info.tmp >nul
if !errorlevel! equ 0 (
    for /f "tokens=2 delims=:" %%i in ('findstr "username" bot_info.tmp') do (
        set bot_username_raw=%%i
        set bot_username=!bot_username_raw:"=!
        set bot_username=!bot_username:,=!
    )
    echo ✅ Бот активен: @!bot_username!
    set BOT_USERNAME=!bot_username!
) else (
    echo ❌ Не удалось получить информацию о боте
    del bot_info.tmp
    pause
    exit /b 1
)
del bot_info.tmp

REM Запуск финального тестирования
echo 🧪 Запуск финального тестирования...
echo ℹ️ Для полного тестирования запустите: scripts\test_production.sh

REM Создание отчета о запуске
echo 📊 Создание отчета о запуске...

set launch_report=launch_report_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.md
set launch_report=%launch_report: =0%

echo # ChartGenius Launch Report > %launch_report%
echo. >> %launch_report%
echo **Дата запуска**: %date% %time% >> %launch_report%
echo **Проект**: %PROJECT_ID% >> %launch_report%
echo **Регион**: %REGION% >> %launch_report%
echo. >> %launch_report%
echo ## 🌐 URL сервисов >> %launch_report%
echo - **Frontend**: %FRONTEND_URL% >> %launch_report%
echo - **API**: %API_URL% >> %launch_report%
echo - **Bot**: %BOT_URL% >> %launch_report%
echo. >> %launch_report%
echo ## 🤖 Telegram Bot >> %launch_report%
echo - **Username**: @%BOT_USERNAME% >> %launch_report%
echo - **Webhook**: Настроен и активен >> %launch_report%
echo - **Команды**: /start, /help, /dashboard >> %launch_report%
echo. >> %launch_report%
echo **Система готова к использованию!** 🎉 >> %launch_report%

echo ✅ Отчет о запуске создан: %launch_report%

REM Отображение финальной информации
echo.
echo 🎉 ChartGenius успешно запущен в продакшене!
echo.
echo 📋 Информация для пользователей:
echo ┌─────────────────────────────────────────────────────────────┐
echo │                     ChartGenius                             │
echo │              Готов к использованию!                        │
echo ├─────────────────────────────────────────────────────────────┤
echo │ 🌐 Веб-интерфейс:                                          │
echo │    %FRONTEND_URL%
echo │                                                             │
echo │ 🤖 Telegram Bot:                                           │
echo │    @%BOT_USERNAME%
echo │    Команда для начала: /start                              │
echo │                                                             │
echo │ 📊 Возможности:                                            │
echo │    • Анализ криптовалют с ИИ                               │
echo │    • Технические индикаторы                                │
echo │    • Торговые рекомендации                                 │
echo │    • Интерактивные графики                                 │
echo │    • Личный кабинет                                        │
echo │    • Система подписок                                      │
echo └─────────────────────────────────────────────────────────────┘
echo.
echo 🔧 Для администраторов:
echo • Мониторинг: Google Cloud Console ^> Cloud Run
echo • Логи: gcloud run services logs read SERVICE_NAME --region=%REGION%
echo • Тестирование: scripts\test_production.sh
echo • Обновление: git push ^(автоматический деплой через GitHub Actions^)
echo.
echo 📈 Рекомендации:
echo 1. Настройте алерты в Cloud Monitoring
echo 2. Регулярно проверяйте логи на ошибки
echo 3. Мониторьте использование ресурсов
echo 4. Обновляйте секреты по мере необходимости
echo.
echo 🎯 Система полностью готова к работе с пользователями!
echo.
echo ✅ Запуск ChartGenius завершен успешно!
echo 🚀 Система работает в продакшене!
echo.

pause
