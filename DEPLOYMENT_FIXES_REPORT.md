# Отчет об исправлении проблем деплоя ChartGenius

## Исправленные проблемы

### 1. ✅ Проблемы с путями в Dockerfile
**Проблема**: Пути `../../` не работали при сборке из production папки
**Решение**: 
- Исправлены пути к requirements.txt в обоих Dockerfile
- Обновлены команды запуска для правильного указания на production файлы
- Контекст сборки остается корневой папкой проекта

### 2. ✅ Проблема с переменной PORT в Cloud Run
**Проблема**: Cloud Run резервирует переменную PORT, что вызывало конфликты
**Решение**:
- Изменена переменная PORT на SERVER_PORT в Dockerfile
- Обновлена конфигурация backend для использования SERVER_PORT с fallback на PORT
- Обновлена конфигурация bot для использования SERVER_PORT с fallback на PORT
- Обновлены health check команды для использования правильного порта
- Обновлен deploy скрипт для установки SERVER_PORT=8080

### 3. ✅ Проблема с невидимыми символами \r в webhook URL
**Проблема**: Невидимые символы \r (возврат каретки) в URL webhook могли вызывать ошибки
**Решение**:
- Добавлена функция `_clean_url()` в ProductionBotConfig
- Все URL (webapp_url и webhook_url) теперь очищаются от \r и \n символов
- Добавлено логирование URL с repr() для отладки невидимых символов

### 4. ✅ Проблемы с requirements.txt
**Проблема**: Неправильные пути к requirements.txt в Dockerfile
**Решение**:
- Скопированы requirements.txt файлы в production папки
- Обновлены пути в Dockerfile для корректного доступа к файлам

## Внесенные изменения

### Файлы Dockerfile
- `production/backend/Dockerfile`: Исправлены пути, переменные окружения, health check
- `production/bot/Dockerfile`: Исправлены пути, переменные окружения, health check

### Конфигурационные файлы
- `production/backend/config/production.py`: Обновлена логика получения порта
- `production/bot/app.py`: Добавлена очистка URL, обновлена логика порта, добавлено логирование

### Скрипты деплоя
- `production/deploy-production.sh`: Добавлены переменные SERVER_PORT и USE_WEBHOOK

### Новые файлы
- `production/backend/requirements.txt`: Скопирован из backend/requirements.txt
- `production/bot/requirements.txt`: Скопирован из bot/requirements.txt

## Рекомендации по деплою

### Переменные окружения для Cloud Run
```bash
# Backend
GCP_PROJECT_ID=chartgenius-444017
GCP_REGION=europe-west1
ENVIRONMENT=production
ADMIN_TELEGRAM_ID=299820674
SERVER_PORT=8080

# Bot
GCP_PROJECT_ID=chartgenius-444017
GCP_REGION=europe-west1
ENVIRONMENT=production
ADMIN_TELEGRAM_ID=299820674
SERVER_PORT=8080
USE_WEBHOOK=true
```

### Секреты в Google Cloud Secret Manager
- `openai-api-key`: OpenAI API ключ
- `jwt-secret-key`: JWT секретный ключ
- `cryptocompare-api-key`: CryptoCompare API ключ
- `telegram-bot-token`: Telegram Bot токен

### Команды для деплоя
```bash
# Установка переменных окружения
export GCP_PROJECT_ID=chartgenius-444017
export GCP_REGION=europe-west1
export VERSION=1.0.2

# Запуск деплоя
cd production
./deploy-production.sh
```

## Отладка проблем

### Проверка логов
```bash
# Backend логи
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=chartgenius-api" --limit=50

# Bot логи
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=chartgenius-bot" --limit=50
```

### Проверка health endpoints
```bash
# Backend health check
curl https://chartgenius-api-169129692197.europe-west1.run.app/health

# Bot health check (требует аутентификации)
gcloud run services proxy chartgenius-bot --port=8080 &
curl http://localhost:8080/health
```

### Проверка webhook URL
В логах бота теперь выводится repr() URL, что позволяет увидеть невидимые символы:
```
WebApp URL: 'https://chartgenius-frontend-europe-west1-a.run.app'
Webhook URL: 'https://chartgenius-bot-europe-west1-a.run.app/webhook'
```

## Статус исправлений
- ✅ Dockerfile пути исправлены
- ✅ PORT переменная заменена на SERVER_PORT
- ✅ URL очистка от невидимых символов добавлена
- ✅ Requirements файлы скопированы
- ✅ Deploy скрипт обновлен
- ✅ Логирование для отладки добавлено

Все основные проблемы деплоя исправлены. Система готова к развертыванию в продакшн.
