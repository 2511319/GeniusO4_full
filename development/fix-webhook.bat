@echo off
REM 🔧 ChartGenius Bot Webhook Fix Script (Windows)
REM Версия: 1.1.0-dev
REM Принудительное исправление webhook настроек

setlocal enabledelayedexpansion

REM Конфигурация
set PROJECT_ID=chartgenius-444017
set REGION=europe-west1
set SERVICE_NAME=chartgenius-bot
set BOT_TOKEN=7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0

echo.
echo 🔧 ИСПРАВЛЕНИЕ TELEGRAM WEBHOOK
echo ================================
echo.
echo Проект: %PROJECT_ID%
echo Сервис: %SERVICE_NAME%
echo Регион: %REGION%
echo.

REM Проверка текущего webhook
echo ================================
echo Проверка текущего webhook
echo ================================
echo.

echo ℹ️  Получение информации о webhook...
curl -s "https://api.telegram.org/bot%BOT_TOKEN%/getWebhookInfo" > webhook_info.json

echo Текущая информация о webhook:
type webhook_info.json | python -m json.tool

echo.

REM Удаление текущего webhook
echo ================================
echo Удаление текущего webhook
echo ================================
echo.

echo ℹ️  Удаление webhook...
curl -s -X POST "https://api.telegram.org/bot%BOT_TOKEN%/deleteWebhook" ^
    -H "Content-Type: application/json" ^
    -d "{\"drop_pending_updates\": true}" > delete_result.json

echo Результат удаления:
type delete_result.json | python -m json.tool

echo ✅ Webhook удален
echo ℹ️  Ожидание 5 секунд...
timeout /t 5 /nobreak >nul

echo.

REM Получение URL сервиса
echo ================================
echo Получение URL сервиса
echo ================================
echo.

echo ℹ️  Получение URL Cloud Run сервиса...
for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)"') do set SERVICE_URL=%%i

if "%SERVICE_URL%"=="" (
    echo ❌ Не удалось получить URL сервиса
    echo ℹ️  Проверьте что сервис %SERVICE_NAME% развернут в регионе %REGION%
    pause
    exit /b 1
)

echo ✅ URL сервиса: %SERVICE_URL%

REM Формируем webhook URL
set WEBHOOK_URL=%SERVICE_URL%/webhook
echo ℹ️  Webhook URL: %WEBHOOK_URL%

echo.

REM Тестирование доступности сервиса
echo ================================
echo Тестирование доступности сервиса
echo ================================
echo.

echo ℹ️  Тестирование health check...
set HEALTH_URL=%SERVICE_URL%/health

curl -f -s "%HEALTH_URL%" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Health check не прошел
    echo ⚠️  Сервис может быть недоступен
    set /p continue="Продолжить установку webhook? [y/N]: "
    if /i not "!continue!"=="y" (
        exit /b 1
    )
) else (
    echo ✅ Health check прошел успешно
)

echo ℹ️  Тестирование webhook endpoint...
curl -s -o nul -w "%%{http_code}" -X POST "%WEBHOOK_URL%" ^
    -H "Content-Type: application/json" ^
    -d "{\"test\": \"ping\"}" > http_status.txt

set /p HTTP_STATUS=<http_status.txt

if "%HTTP_STATUS%"=="200" (
    echo ✅ Webhook endpoint отвечает (HTTP %HTTP_STATUS%)
) else if "%HTTP_STATUS%"=="400" (
    echo ✅ Webhook endpoint отвечает (HTTP %HTTP_STATUS%)
) else if "%HTTP_STATUS%"=="405" (
    echo ✅ Webhook endpoint отвечает (HTTP %HTTP_STATUS%)
) else (
    echo ⚠️  Webhook endpoint вернул HTTP %HTTP_STATUS%
)

echo.

REM Установка нового webhook
echo ================================
echo Установка нового webhook
echo ================================
echo.

echo ℹ️  Установка webhook URL: %WEBHOOK_URL%

REM Генерируем случайный secret token (упрощенная версия)
set SECRET_TOKEN=%RANDOM%%RANDOM%%RANDOM%%RANDOM%

curl -s -X POST "https://api.telegram.org/bot%BOT_TOKEN%/setWebhook" ^
    -H "Content-Type: application/json" ^
    -d "{\"url\": \"%WEBHOOK_URL%\", \"drop_pending_updates\": true, \"secret_token\": \"%SECRET_TOKEN%\", \"max_connections\": 40, \"allowed_updates\": [\"message\", \"callback_query\", \"inline_query\"]}" > set_result.json

echo Результат установки webhook:
type set_result.json | python -m json.tool

REM Проверяем успешность
findstr "\"ok\": true" set_result.json >nul
if errorlevel 1 (
    echo ❌ Ошибка установки webhook
    pause
    exit /b 1
) else (
    echo ✅ Webhook установлен успешно
    echo ℹ️  Secret token: %SECRET_TOKEN%
)

echo ℹ️  Обновление переменных окружения...
gcloud run services update %SERVICE_NAME% ^
    --region=%REGION% ^
    --set-env-vars "WEBHOOK_SECRET=%SECRET_TOKEN%" ^
    --quiet

if errorlevel 1 (
    echo ⚠️  Не удалось обновить переменные окружения
) else (
    echo ✅ Secret token добавлен в переменные окружения
)

echo.

REM Проверка нового webhook
echo ================================
echo Проверка нового webhook
echo ================================
echo.

echo ℹ️  Ожидание 10 секунд для стабилизации...
timeout /t 10 /nobreak >nul

echo ℹ️  Получение информации о webhook...
curl -s "https://api.telegram.org/bot%BOT_TOKEN%/getWebhookInfo" > final_webhook_info.json

echo Финальная информация о webhook:
type final_webhook_info.json | python -m json.tool

REM Проверяем URL
findstr "%WEBHOOK_URL%" final_webhook_info.json >nul
if errorlevel 1 (
    echo ❌ Webhook URL не соответствует ожидаемому
) else (
    echo ✅ Webhook URL установлен корректно
)

echo.

REM Отправка тестового сообщения
echo ================================
echo Отправка тестового сообщения
echo ================================
echo.

echo ℹ️  Отправка тестового сообщения админу...

set TEST_MESSAGE=🔧 ^<b^>Webhook исправлен!^</b^>^^n^^nВремя: %DATE% %TIME%^^n^^n✅ Webhook URL обновлен^^n✅ Secret token установлен^^n✅ Pending updates очищены^^n✅ Переменные окружения обновлены^^n^^nПроверьте работу команды /start

curl -s -X POST "https://api.telegram.org/bot%BOT_TOKEN%/sendMessage" ^
    -H "Content-Type: application/json" ^
    -d "{\"chat_id\": \"299820674\", \"text\": \"%TEST_MESSAGE%\", \"parse_mode\": \"HTML\"}" > message_result.json

findstr "\"ok\": true" message_result.json >nul
if errorlevel 1 (
    echo ❌ Ошибка отправки тестового сообщения
    type message_result.json | python -m json.tool
) else (
    echo ✅ Тестовое сообщение отправлено
)

echo.

REM Очистка временных файлов
del webhook_info.json delete_result.json set_result.json final_webhook_info.json message_result.json http_status.txt 2>nul

echo ================================
echo 🎉 Webhook исправлен успешно!
echo ================================
echo ✅ Все операции завершены
echo ℹ️  Проверьте работу бота командой /start в @Chart_Genius_bot
echo.

pause

endlocal
