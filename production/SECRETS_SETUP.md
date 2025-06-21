# Настройка секретов для ChartGenius Production

## 🔐 Обзор

В продакшн версии ChartGenius все секреты хранятся в Google Cloud Secret Manager для обеспечения безопасности.

## 📋 Необходимые секреты

### 1. OpenAI API Key
```bash
echo "your-openai-api-key" | gcloud secrets create openai-api-key --data-file=-
```

**Где получить:**
- Зарегистрируйтесь на https://platform.openai.com/
- Перейдите в API Keys
- Создайте новый ключ

### 2. JWT Secret Key
```bash
# Генерация случайного ключа
openssl rand -base64 32 | gcloud secrets create jwt-secret-key --data-file=-

# Или создайте свой ключ
echo "your-super-secret-jwt-key-min-32-chars" | gcloud secrets create jwt-secret-key --data-file=-
```

### 3. CryptoCompare API Key
```bash
echo "your-cryptocompare-api-key" | gcloud secrets create cryptocompare-api-key --data-file=-
```

**Где получить:**
- Зарегистрируйтесь на https://www.cryptocompare.com/
- Перейдите в API section
- Создайте новый API ключ

### 4. Telegram Bot Token
```bash
echo "your-telegram-bot-token" | gcloud secrets create telegram-bot-token --data-file=-
```

**Где получить:**
- Напишите @BotFather в Telegram
- Используйте команду `/newbot`
- Следуйте инструкциям для создания бота
- Скопируйте полученный токен

## 🔧 Проверка секретов

Проверьте, что все секреты созданы:

```bash
gcloud secrets list
```

Должны быть видны:
- openai-api-key
- jwt-secret-key
- cryptocompare-api-key
- telegram-bot-token

## 🔄 Обновление секретов

Для обновления существующего секрета:

```bash
echo "new-secret-value" | gcloud secrets versions add SECRET_NAME --data-file=-
```

## 🔍 Просмотр секретов

**ВНИМАНИЕ:** Будьте осторожны при просмотре секретов в продакшн!

```bash
gcloud secrets versions access latest --secret="SECRET_NAME"
```

## 🛡️ Права доступа

Убедитесь, что у сервисного аккаунта Cloud Run есть права на чтение секретов:

```bash
# Получение email сервисного аккаунта
gcloud run services describe SERVICE_NAME --region=REGION --format="value(spec.template.spec.serviceAccountName)"

# Добавление роли Secret Manager Secret Accessor
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
    --role="roles/secretmanager.secretAccessor"
```

## 🔒 Безопасность

### Рекомендации:
1. **Никогда не коммитьте секреты в Git**
2. **Используйте принцип минимальных привилегий**
3. **Регулярно ротируйте секреты**
4. **Мониторьте доступ к секретам**
5. **Используйте разные секреты для разных окружений**

### Аудит доступа:
```bash
# Просмотр логов доступа к секретам
gcloud logging read "resource.type=gce_instance AND protoPayload.serviceName=secretmanager.googleapis.com" --limit=50
```

## 🚨 Восстановление

Если секрет был скомпрометирован:

1. **Немедленно создайте новую версию секрета**
2. **Перезапустите все сервисы**
3. **Отзовите старый ключ у провайдера**
4. **Проверьте логи на подозрительную активность**

```bash
# Быстрое обновление секрета
echo "new-secure-value" | gcloud secrets versions add SECRET_NAME --data-file=-

# Перезапуск сервисов
gcloud run services update chartgenius-api --region=europe-west1
gcloud run services update chartgenius-bot --region=europe-west1
```

## 📞 Поддержка

При проблемах с секретами:
1. Проверьте права доступа IAM
2. Убедитесь, что Secret Manager API включен
3. Проверьте логи Cloud Run сервисов
4. Обратитесь к документации Google Cloud Secret Manager
