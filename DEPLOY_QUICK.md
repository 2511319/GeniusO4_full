# 🚀 Быстрый деплой в Google Cloud Run

## Предварительные требования

1. **Google Cloud SDK** установлен и настроен
2. **Docker** установлен (для локальной сборки)
3. **Проект Google Cloud** создан

## Шаг 1: Настройка Google Cloud

```bash
# Установите gcloud CLI если еще не установлен
# https://cloud.google.com/sdk/docs/install

# Авторизуйтесь
gcloud auth login

# Создайте новый проект или используйте существующий
gcloud projects create geniuso4-project --name="GeniusO4"
gcloud config set project geniuso4-project

# Включите биллинг для проекта в консоли GCP
# https://console.cloud.google.com/billing
```

## Шаг 2: Быстрый деплой

```bash
# Сделайте скрипт исполняемым (Linux/Mac)
chmod +x deploy_gcp.sh

# Запустите деплой
./deploy_gcp.sh
```

**Для Windows:**
```bash
bash deploy_gcp.sh
```

## Шаг 3: Что происходит автоматически

1. ✅ Включаются необходимые API (Cloud Build, Cloud Run, Secret Manager)
2. ✅ Создаются секреты с API ключами
3. ✅ Собираются Docker образы для всех сервисов
4. ✅ Деплоятся 3 сервиса в Cloud Run:
   - `geniuso4-api` - Backend API
   - `geniuso4-bot` - Telegram Bot
   - `geniuso4-frontend` - React Frontend
5. ✅ Настраивается webhook для Telegram бота

## Шаг 4: Результат

После успешного деплоя вы получите:

```
🎉 Деплой успешно завершен!

📊 Frontend: https://geniuso4-frontend-xxx-uc.a.run.app
🔧 Backend API: https://geniuso4-api-xxx-uc.a.run.app
🤖 Telegram Bot: https://geniuso4-bot-xxx-uc.a.run.app
📚 API Docs: https://geniuso4-api-xxx-uc.a.run.app/docs

✅ Все готово! Откройте Frontend URL для начала работы
```

## Шаг 5: Тестирование

1. **Веб-интерфейс**: Откройте Frontend URL
2. **Telegram Bot**: Найдите @Chart_Genius_bot и отправьте `/start`
3. **API**: Откройте API Docs URL для тестирования эндпоинтов

## Troubleshooting

### Ошибка "Project not found"
```bash
gcloud config set project YOUR_PROJECT_ID
gcloud auth application-default login
```

### Ошибка "Billing not enabled"
- Включите биллинг в [GCP Console](https://console.cloud.google.com/billing)

### Ошибка "API not enabled"
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### Telegram Bot не отвечает
- Проверьте логи: `gcloud run services logs read geniuso4-bot --region=us-central1`
- Убедитесь, что webhook настроен правильно

## Мониторинг

```bash
# Логи API
gcloud run services logs read geniuso4-api --region=us-central1

# Логи Bot
gcloud run services logs read geniuso4-bot --region=us-central1

# Статус сервисов
gcloud run services list --region=us-central1
```

## Обновление

Для обновления просто запустите деплой снова:
```bash
./deploy_gcp.sh
```

Cloud Build автоматически пересоберет и задеплоит обновленные сервисы.

---

**Время деплоя**: ~5-10 минут  
**Стоимость**: ~$0-5/месяц при небольшом трафике (Cloud Run платит только за использование)
