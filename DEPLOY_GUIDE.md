# Руководство по развертыванию ChartGenius в Google Cloud Platform

## Проект: chartgenius-444017

Это руководство поможет вам развернуть полную систему ChartGenius в Google Cloud Platform.

## 📋 Предварительные требования

### 1. Установленное ПО
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- [Docker](https://docs.docker.com/get-docker/)
- [Python 3.8+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)
- [Git](https://git-scm.com/)

### 2. Учетные записи и токены
- Аккаунт Google Cloud с активированным биллингом
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))
- OpenAI API Key (получить на [platform.openai.com](https://platform.openai.com/))
- CryptoCompare API Key (опционально, получить на [cryptocompare.com](https://cryptocompare.com/))

## 🚀 Быстрое развертывание

### Автоматическая настройка (Linux/macOS)
```bash
# Клонируйте репозиторий
git clone <repository-url>
cd GeniusO4_esc

# Запустите полную настройку
./scripts/setup_complete.sh
```

### Ручная настройка (Windows/Linux/macOS)

#### Шаг 1: Настройка Google Cloud
```bash
# Установите проект по умолчанию
gcloud config set project chartgenius-444017

# Запустите настройку GCP
bash scripts/setup_gcp.sh
```

#### Шаг 2: Обновление секретов
```bash
# Интерактивное обновление секретов
bash scripts/update_secrets.sh
```

#### Шаг 3: Настройка Firestore
```bash
# Создание коллекций и примеров данных
python3 scripts/setup_firestore.py
```

#### Шаг 4: Развертывание приложения
```bash
# Ручное развертывание всех сервисов
bash scripts/deploy_manual.sh
```

#### Шаг 5: Настройка Telegram бота
```bash
# Установите токен бота
export TELEGRAM_BOT_TOKEN="your_bot_token"

# Настройте webhook и команды
bash scripts/setup_telegram.sh
```

## 🔧 Развертывание через GitHub Actions

### 1. Настройка GitHub Secrets
Добавьте следующие секреты в настройки GitHub репозитория:

- `GCP_PROJECT_ID`: `chartgenius-444017`
- `GCP_SA_KEY`: JSON ключ сервисного аккаунта (содержимое файла `github-actions-key.json`)

### 2. Автоматическое развертывание
GitHub Actions автоматически развернет приложение при push в main ветку.

## 📊 Структура развертывания

### Cloud Run сервисы
1. **chartgenius-api** - Backend API (FastAPI)
   - CPU: 1 vCPU
   - Memory: 1Gi
   - Max instances: 10

2. **chartgenius-frontend** - Frontend (React)
   - CPU: 1 vCPU
   - Memory: 512Mi
   - Max instances: 5

3. **chartgenius-bot** - Telegram Bot
   - CPU: 1 vCPU
   - Memory: 512Mi
   - Max instances: 5

### Firestore коллекции
- `users` - Пользователи Telegram
- `subscriptions` - Подписки пользователей
- `analyses` - Результаты анализа (TTL: 30 дней)

### Secret Manager секреты
- `JWT_SECRET_KEY` - Ключ для JWT токенов
- `TELEGRAM_BOT_TOKEN` - Токен Telegram бота
- `OPENAI_API_KEY` - Ключ OpenAI API
- `CRYPTOCOMPARE_API_KEY` - Ключ CryptoCompare API

## 🔍 Проверка развертывания

### 1. Проверка сервисов
```bash
# Статус всех сервисов
gcloud run services list --region=us-central1

# URL сервисов
gcloud run services describe chartgenius-api --region=us-central1 --format="value(status.url)"
gcloud run services describe chartgenius-frontend --region=us-central1 --format="value(status.url)"
gcloud run services describe chartgenius-bot --region=us-central1 --format="value(status.url)"
```

### 2. Проверка секретов
```bash
# Список секретов
gcloud secrets list --filter="labels.project=chartgenius"

# Проверка версий секретов
gcloud secrets versions list JWT_SECRET_KEY
```

### 3. Проверка Firestore
```bash
# Проверка через Python
python3 -c "
from google.cloud import firestore
db = firestore.Client()
print('Collections:', [c.id for c in db.collections()])
"
```

## 📝 Тестирование

### 1. Frontend
- Откройте URL frontend сервиса
- Проверьте аутентификацию через Telegram
- Протестируйте личный кабинет

### 2. Telegram Bot
- Найдите бота в Telegram
- Отправьте `/start`
- Протестируйте получение анализа
- Проверьте переход в веб-интерфейс

### 3. API
```bash
# Проверка health endpoint
curl https://chartgenius-api-us-central1-uc.a.run.app/health
```

## 🔧 Отладка

### Просмотр логов
```bash
# Логи API
gcloud run services logs read chartgenius-api --region=us-central1

# Логи Bot
gcloud run services logs read chartgenius-bot --region=us-central1

# Логи Frontend
gcloud run services logs read chartgenius-frontend --region=us-central1
```

### Общие проблемы

#### 1. Холодный старт
- **Проблема**: Первый запрос занимает много времени
- **Решение**: Это нормально для Cloud Run, последующие запросы будут быстрее

#### 2. Ошибки аутентификации
- **Проблема**: JWT токены не работают
- **Решение**: Проверьте секрет `JWT_SECRET_KEY`

#### 3. Telegram webhook не работает
- **Проблема**: Бот не отвечает на сообщения
- **Решение**: Проверьте настройку webhook и логи bot сервиса

#### 4. Ошибки Firestore
- **Проблема**: Ошибки доступа к базе данных
- **Решение**: Проверьте права доступа и настройки Firestore

## 🔄 Обновление

### Автоматическое обновление
Push в main ветку автоматически запустит развертывание через GitHub Actions.

### Ручное обновление
```bash
# Обновление конкретного сервиса
gcloud run deploy chartgenius-api --source backend/ --region us-central1
```

## 🛡️ Безопасность

### 1. Секреты
- Все секреты хранятся в Google Secret Manager
- Регулярно обновляйте API ключи
- Используйте принцип минимальных привилегий

### 2. Доступ
- Cloud Run сервисы доступны публично (необходимо для Telegram webhook)
- Аутентификация через JWT токены
- Firestore защищен правилами безопасности

### 3. Мониторинг
- Настройте алерты в Google Cloud Monitoring
- Регулярно проверяйте логи на подозрительную активность

## 💰 Стоимость

### Примерная стоимость (при умеренном использовании):
- **Cloud Run**: $5-20/месяц
- **Firestore**: $1-5/месяц
- **Secret Manager**: $0.06/месяц
- **Networking**: $1-3/месяц

**Общая стоимость**: $7-28/месяц

### Оптимизация затрат:
- Используйте минимальные ресурсы для начала
- Настройте автоматическое масштабирование
- Мониторьте использование ресурсов

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи сервисов
2. Убедитесь в правильности настройки секретов
3. Проверьте статус сервисов в Google Cloud Console
4. Обратитесь к документации Google Cloud Run
