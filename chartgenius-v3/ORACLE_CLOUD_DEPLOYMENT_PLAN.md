# 🚀 Oracle Cloud Deployment Plan - ChartGenius v3

Детальный план развертывания backend на Oracle Always Free Tier с локальной разработкой frontend.

## 🎯 Цели Deployment

1. **Backend на Oracle Cloud** - Production-ready API
2. **Frontend локально** - Быстрая разработка
3. **Telegram Bot интеграция** - WebApp + Payments
4. **Oracle AJD** - Существующая база ChartGenius2
5. **SSL/HTTPS** - Безопасное соединение

## 🏗️ Архитектура Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                    Oracle Cloud Always Free                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Compute VM    │  │  Load Balancer  │  │  Oracle AJD  │ │
│  │  (ARM/x86)     │  │   (Optional)    │  │ ChartGenius2 │ │
│  │                 │  │                 │  │              │ │
│  │  Docker:        │  │  SSL Termination│  │  JSON Store  │ │
│  │  - Backend API  │  │  - chartgenius  │  │  - Users     │ │
│  │  - Redis Cache  │  │    .online      │  │  - Analyses  │ │
│  │  - Nginx Proxy  │  │                 │  │  - Payments  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS API Calls
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Local Development                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Frontend      │  │   Telegram      │  │   Browser    │ │
│  │   React 19      │  │   WebApp        │  │   DevTools   │ │
│  │   Vite Dev      │  │   Testing       │  │   Hot Reload │ │
│  │   localhost:5173│  │                 │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Deployment Checklist

### ✅ ФАЗА 1: Подготовка (30 мин)
- [x] Создан production .env файл
- [x] Оптимизирован Dockerfile под Always Free
- [x] Настроен docker-compose.yml
- [x] Создан deployment скрипт
- [x] Подготовлены Kubernetes манифесты

### ⏳ ФАЗА 2: Oracle Cloud Setup (1-2 часа)
- [ ] Создать Compute Instance (Always Free)
- [ ] Настроить Security Groups
- [ ] Установить Docker и Docker Compose
- [ ] Настроить домен chartgenius.online
- [ ] Получить SSL сертификаты

### ⏳ ФАЗА 3: Backend Deployment (1 час)
- [ ] Загрузить код на Oracle VM
- [ ] Собрать Docker образы
- [ ] Запустить docker-compose
- [ ] Проверить health endpoints
- [ ] Настроить мониторинг

### ⏳ ФАЗА 4: Telegram Integration (30 мин)
- [ ] Настроить Telegram Bot webhooks
- [ ] Протестировать WebApp интеграцию
- [ ] Настроить Telegram Stars payments
- [ ] Проверить webhook обработку

### ⏳ ФАЗА 5: Frontend Integration (30 мин)
- [ ] Обновить frontend конфигурацию
- [ ] Протестировать API интеграцию
- [ ] Проверить CORS настройки
- [ ] Запустить integration тесты

## 🛠️ Пошаговые инструкции

### 1. Oracle Cloud Compute Instance

**Создание VM:**
```bash
# Спецификации Always Free
- Shape: VM.Standard.A1.Flex (ARM) или VM.Standard.E2.1.Micro (x86)
- Memory: 1GB (E2.1.Micro) или до 24GB (A1.Flex)
- Storage: 47GB Boot Volume
- OS: Ubuntu 22.04 LTS
```

**Настройка Security Groups:**
```bash
# Ingress Rules
- Port 22 (SSH): 0.0.0.0/0
- Port 80 (HTTP): 0.0.0.0/0  
- Port 443 (HTTPS): 0.0.0.0/0
- Port 8000 (API): 0.0.0.0/0 (временно)

# Egress Rules
- All traffic: 0.0.0.0/0
```

### 2. VM Setup

**Подключение к VM:**
```bash
ssh -i ~/.ssh/oracle_key ubuntu@<VM_PUBLIC_IP>
```

**Установка Docker:**
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Перезагрузка для применения изменений
sudo reboot
```

### 3. Code Deployment

**Загрузка кода:**
```bash
# Клонирование репозитория
git clone <your-repo-url> chartgenius-v3
cd chartgenius-v3

# Или загрузка через SCP
scp -i ~/.ssh/oracle_key -r chartgenius-v3/ ubuntu@<VM_IP>:~/
```

**Настройка environment:**
```bash
# Копирование production конфигурации
cp backend/.env.production backend/.env

# Проверка конфигурации
cat backend/.env
```

### 4. Docker Deployment

**Сборка и запуск:**
```bash
# Сборка образов
docker-compose build

# Запуск в production режиме
docker-compose up -d

# Проверка статуса
docker-compose ps
docker-compose logs -f backend
```

**Проверка health:**
```bash
# Локальная проверка
curl http://localhost:8000/health

# Внешняя проверка (с другой машины)
curl http://<VM_PUBLIC_IP>:8000/health
```

### 5. Domain & SSL Setup

**DNS настройка:**
```bash
# A Records
chartgenius.online → <VM_PUBLIC_IP>
api.chartgenius.online → <VM_PUBLIC_IP>
*.chartgenius.online → <VM_PUBLIC_IP>
```

**SSL сертификаты (Let's Encrypt):**
```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получение сертификатов
sudo certbot certonly --standalone -d chartgenius.online -d api.chartgenius.online

# Автоматическое обновление
sudo crontab -e
# Добавить: 0 12 * * * /usr/bin/certbot renew --quiet
```

**Nginx конфигурация:**
```nginx
# /etc/nginx/sites-available/chartgenius
server {
    listen 80;
    server_name chartgenius.online api.chartgenius.online;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.chartgenius.online;
    
    ssl_certificate /etc/letsencrypt/live/chartgenius.online/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/chartgenius.online/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6. Telegram Bot Setup

**Webhook настройка:**
```bash
# Запуск скрипта настройки
chmod +x setup-telegram-bot.sh
./setup-telegram-bot.sh

# Проверка webhook
curl "https://api.telegram.org/bot7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0/getWebhookInfo"
```

### 7. Frontend Development Setup

**Локальная настройка:**
```bash
cd chartgenius-v3-frontend

# Установка зависимостей
npm install

# Настройка environment
cp .env.development .env

# Запуск dev сервера
npm run dev
```

**Проверка интеграции:**
```bash
# Из корневой директории
chmod +x test-integration.sh
./test-integration.sh
```

## 📊 Мониторинг и Логирование

### 📈 Health Monitoring

**Endpoints для мониторинга:**
```bash
# Простая проверка
curl https://api.chartgenius.online/health

# Детальная проверка
curl https://api.chartgenius.online/api/health

# Статистика системы
curl -H "Authorization: Bearer <admin_token>" \
     https://api.chartgenius.online/api/admin/stats/system
```

**Docker мониторинг:**
```bash
# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats

# Логи
docker-compose logs -f --tail=100
```

### 📝 Логирование

**Настройка логов:**
```bash
# Ротация логов
sudo nano /etc/logrotate.d/chartgenius

# Содержимое:
/home/ubuntu/chartgenius-v3/backend/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 ubuntu ubuntu
}
```

**Мониторинг логов:**
```bash
# Backend логи
tail -f backend/logs/chartgenius.log

# Docker логи
docker-compose logs -f backend

# System логи
sudo journalctl -u docker -f
```

## 🔧 Troubleshooting

### ❌ Частые проблемы

**1. Контейнер не запускается:**
```bash
# Проверить логи
docker-compose logs backend

# Проверить конфигурацию
docker-compose config

# Пересобрать образ
docker-compose build --no-cache backend
```

**2. База данных недоступна:**
```bash
# Проверить подключение
docker-compose exec backend python -c "
from config.database import init_database
import asyncio
asyncio.run(init_database())
"
```

**3. SSL проблемы:**
```bash
# Проверить сертификаты
sudo certbot certificates

# Обновить сертификаты
sudo certbot renew

# Проверить Nginx конфигурацию
sudo nginx -t
```

**4. CORS ошибки:**
```bash
# Проверить CORS заголовки
curl -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS https://api.chartgenius.online/api/analysis/analyze
```

## 🎯 Performance Optimization

### ⚡ Always Free Optimization

**Resource limits:**
```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.1'
```

**Database optimization:**
```python
# Oracle connection pool
ORACLE_POOL_MIN=1
ORACLE_POOL_MAX=3
ORACLE_POOL_INCREMENT=1
```

**Redis optimization:**
```bash
# Redis memory limit
redis-server --maxmemory 128mb --maxmemory-policy allkeys-lru
```

## 🚀 Deployment Commands

**Быстрый deployment:**
```bash
# Запуск deployment скрипта
chmod +x deploy-oracle-cloud.sh
./deploy-oracle-cloud.sh
```

**Ручной deployment:**
```bash
# 1. Сборка
docker-compose build

# 2. Запуск
docker-compose up -d

# 3. Проверка
curl https://api.chartgenius.online/health

# 4. Telegram setup
./setup-telegram-bot.sh

# 5. Integration test
./test-integration.sh
```

## ✅ Success Criteria

**Backend готов когда:**
- ✅ Health endpoints отвечают 200 OK
- ✅ Oracle AJD подключение работает
- ✅ AI анализ возвращает 24 объекта
- ✅ Telegram webhooks настроены
- ✅ SSL сертификаты активны

**Frontend готов когда:**
- ✅ Dev сервер запускается на localhost:5173
- ✅ API запросы проходят через HTTPS
- ✅ Telegram WebApp аутентификация работает
- ✅ Все 22 компонента анализа отображаются
- ✅ Integration тесты проходят

**🎉 Deployment завершен успешно!**
