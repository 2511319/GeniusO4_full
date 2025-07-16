# ChartGenius v3 Frontend Integration Guide

## Обзор

Данное руководство предназначено для разработчиков, которые хотят создать собственный фронтенд для ChartGenius v3 или интегрировать существующий фронтенд с бэкендом ChartGenius v3.

## Технические требования

### Стек технологий
- **Frontend**: React 19 + Tailwind CSS 4.0
- **Charts**: TradingView Lightweight Charts 5.0.8
- **Backend**: FastAPI + Python 3.11+
- **Database**: Oracle Always Free Tier
- **Deployment**: Docker + Oracle Cloud Infrastructure
- **Authentication**: Telegram WebApp
- **Payments**: Telegram Stars

### Системные требования
- Node.js 18+ для фронтенда
- Python 3.11+ для бэкенда
- Docker для развертывания
- Oracle Cloud Account (Always Free Tier)

## API Endpoints

### Базовый URL
```
Production: https://chartgenius.online/api
Development: http://localhost:8000/api
```

### Аутентификация

#### POST /api/auth/telegram
Аутентификация через Telegram WebApp

**Request:**
```json
{
  "init_data": "telegram_webapp_init_data_string",
  "user_id": 299820674
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "user": {
    "id": 299820674,
    "username": "username",
    "subscription_status": "active"
  }
}
```

### Анализ

#### POST /api/analysis/analyze
Запуск анализа криптовалютной пары

**Headers:**
```
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request:**
```json
{
  "symbol": "BTCUSDT",
  "interval": "1h",
  "limit": 100
}
```

**Response:** (24 AI объекта анализа)
```json
{
  "primary_analysis": {
    "trend": "bullish",
    "confidence": 0.85,
    "summary": "Анализ показывает..."
  },
  "support_resistance_levels": {
    "supports": [
      {
        "level": 104250.75,
        "date": "2025-01-16 15:00:00",
        "strength": 0.9
      }
    ],
    "resistances": [
      {
        "level": 105800.25,
        "date": "2025-01-16 18:00:00", 
        "strength": 0.8
      }
    ]
  },
  "fibonacci_analysis": {
    "based_on_local_trend": {
      "start_point": {
        "date": "2025-01-15 12:00:00",
        "price": 103200.00
      },
      "end_point": {
        "date": "2025-01-16 08:00:00",
        "price": 105400.00
      },
      "levels": {
        "0%": 103200.00,
        "23.6%": 103719.20,
        "38.2%": 104040.80,
        "50%": 104300.00,
        "61.8%": 104559.20,
        "100%": 105400.00
      }
    }
  },
  "indicators_analysis": {
    "rsi": {
      "value": 65.4,
      "signal": "neutral",
      "interpretation": "RSI находится в нейтральной зоне"
    },
    "macd": {
      "macd_line": 245.67,
      "signal_line": 198.34,
      "histogram": 47.33,
      "signal": "bullish"
    }
  },
  "price_prediction": {
    "virtual_candles": [
      {
        "timestamp": 1737043200,
        "datetime": "2025-01-16 20:00:00",
        "open": 104950.75,
        "high": 105200.00,
        "low": 104800.50,
        "close": 105100.25,
        "volume": 1250.75
      }
    ]
  },
  "recommendations": [
    {
      "strategy": "Long Position",
      "entry_price": 104900.00,
      "stop_loss": 104200.00,
      "take_profit": 106500.00,
      "risk_reward_ratio": 3.7,
      "confidence": 0.82
    }
  ]
}
```

### Подписки

#### GET /api/subscription/status
Проверка статуса подписки

#### POST /api/subscription/create-payment
Создание платежа через Telegram Stars

### Административные функции

#### GET /api/admin/stats
Статистика системы (только для админов)

## OHLCV Data Format

### Входящие данные (CryptoCompare API)
```json
[
  {
    "timestamp": 1737043200,
    "datetime": "2025-01-16 20:00:00",
    "open": 104877.59,
    "high": 105200.25,
    "low": 104650.30,
    "close": 104950.75,
    "volume": 1250.50
  }
]
```

### Формат для TradingView Charts
```javascript
const chartData = ohlcvData.map(candle => ({
  time: candle.timestamp,
  open: candle.open,
  high: candle.high,
  low: candle.low,
  close: candle.close,
  volume: candle.volume
}));
```

## TradingView Charts 5.0.8 Integration

### Установка
```bash
npm install lightweight-charts@5.0.8
```

### Базовая настройка
```javascript
import { createChart } from 'lightweight-charts';

const chart = createChart(container, {
  width: 800,
  height: 400,
  layout: {
    background: { color: '#1a1a1a' },
    textColor: '#ffffff',
  },
  grid: {
    vertLines: { color: '#2a2a2a' },
    horzLines: { color: '#2a2a2a' },
  },
  timeScale: {
    timeVisible: true,
    secondsVisible: false,
  },
});

const candlestickSeries = chart.addCandlestickSeries({
  upColor: '#00ff88',
  downColor: '#ff4444',
  borderVisible: false,
  wickUpColor: '#00ff88',
  wickDownColor: '#ff4444',
});
```

### Отрисовка элементов анализа

#### Support/Resistance (Лучи)
```javascript
// Поддержка - зеленые лучи
const supportLine = chart.addLineSeries({
  color: '#22c55e',
  lineWidth: 2,
  lineStyle: 0, // solid
});

const supportData = [
  { time: startTimestamp, value: supportLevel },
  { time: futureTimestamp, value: supportLevel }
];
supportLine.setData(supportData);
```

#### Fibonacci (Прямоугольные области)
```javascript
// Фибоначчи - желтые прямоугольные области
const fibArea = chart.addAreaSeries({
  topColor: 'rgba(255, 193, 7, 0.2)',
  bottomColor: 'rgba(255, 193, 7, 0.1)',
  lineColor: '#ffc107',
  lineWidth: 2,
});

const fibData = [
  { time: startTime, value: topPrice },
  { time: endTime, value: bottomPrice }
];
fibArea.setData(fibData);
```

## CORS Configuration

### Разрешенные домены
```python
# backend/config/config.py
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173", 
    "http://localhost:5174",
    "https://your-frontend-domain.com",
    "https://chartgenius.online"
]
```

### Настройка в FastAPI
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## Telegram Integration

### WebApp инициализация
```javascript
// Telegram WebApp SDK
import { WebApp } from '@twa-dev/sdk';

// Инициализация
WebApp.ready();

// Получение данных пользователя
const initData = WebApp.initData;
const user = WebApp.initDataUnsafe.user;

// Отправка данных для аутентификации
const authResponse = await fetch('/api/auth/telegram', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    init_data: initData,
    user_id: user.id
  })
});
```

### Telegram Stars Payments
```javascript
// Создание платежа
const paymentResponse = await fetch('/api/subscription/create-payment', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    plan: 'premium',
    amount: 100 // Telegram Stars
  })
});

// Обработка платежа
WebApp.openInvoice(paymentResponse.invoice_link, (status) => {
  if (status === 'paid') {
    // Обновить статус подписки
    updateSubscriptionStatus();
  }
});
```

## Oracle Always Free Tier Limitations

### Ресурсы
- **Compute**: VM.Standard.E2.1.Micro (1 OCPU, 1GB RAM) или VM.Standard.A1.Flex (ARM)
- **Storage**: 47GB Boot Volume
- **Network**: 10TB outbound transfer/month
- **Database**: 2 Always Free Autonomous Databases

### Открытые порты
- 22 (SSH)
- 80 (HTTP)
- 443 (HTTPS)
- 8000 (Backend API)

### Оптимизация для ограниченных ресурсов
```python
# Настройки для экономии памяти
WORKERS = 1
MAX_CONNECTIONS = 10
CACHE_SIZE = 100
REQUEST_TIMEOUT = 30
```

## Docker Deployment

### Dockerfile (Backend)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - ORACLE_DSN=${ORACLE_DSN}
    volumes:
      - ./oracle_wallet:/app/oracle_wallet:ro
```

## Nginx Configuration

### Reverse Proxy Setup
```nginx
server {
    listen 80;
    server_name chartgenius.online;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name chartgenius.online;

    ssl_certificate /etc/letsencrypt/live/chartgenius.online/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/chartgenius.online/privkey.pem;

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        # Frontend static files or proxy to frontend server
        root /var/www/chartgenius-frontend;
        try_files $uri $uri/ /index.html;
    }
}
```

## SSL Configuration (Let's Encrypt)

### Установка сертификата
```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d chartgenius.online

# Автообновление
sudo crontab -e
# Добавить: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Deployment Instructions

### 1. Подготовка Oracle Cloud Instance
```bash
# Подключение по SSH
ssh -i ~/.ssh/oracle_key ubuntu@89.168.72.122

# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
```

### 2. Настройка домена
```bash
# DNS A-record уже настроен:
# chartgenius.online -> 89.168.72.122
```

### 3. Развертывание приложения
```bash
# Клонирование репозитория
git clone https://github.com/2511319/chartgenius-v3.git
cd chartgenius-v3

# Настройка переменных окружения
cp backend/.env.example backend/.env
# Отредактировать .env файл

# Запуск через Docker Compose
docker-compose up -d

# Настройка Nginx
sudo apt install nginx
sudo cp nginx.conf /etc/nginx/sites-available/chartgenius
sudo ln -s /etc/nginx/sites-available/chartgenius /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Настройка SSL
sudo certbot --nginx -d chartgenius.online
```

### 4. Мониторинг и логирование
```bash
# Просмотр логов
docker-compose logs -f backend

# Мониторинг ресурсов
docker stats

# Проверка статуса
curl https://chartgenius.online/api/health
```

## API Examples

### Полный пример интеграции
```javascript
class ChartGeniusAPI {
  constructor(baseURL, token) {
    this.baseURL = baseURL;
    this.token = token;
  }

  async authenticate(initData, userId) {
    const response = await fetch(`${this.baseURL}/auth/telegram`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ init_data: initData, user_id: userId })
    });
    const data = await response.json();
    this.token = data.access_token;
    return data;
  }

  async analyze(symbol, interval = '1h', limit = 100) {
    const response = await fetch(`${this.baseURL}/analysis/analyze`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ symbol, interval, limit })
    });
    return await response.json();
  }

  async getSubscriptionStatus() {
    const response = await fetch(`${this.baseURL}/subscription/status`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    return await response.json();
  }
}

// Использование
const api = new ChartGeniusAPI('https://chartgenius.online/api');
const analysis = await api.analyze('BTCUSDT', '1h');
```

## Error Handling

### Стандартные коды ошибок
- `400` - Неверный запрос
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Не найдено
- `429` - Превышен лимит запросов
- `500` - Внутренняя ошибка сервера

### Пример обработки ошибок
```javascript
try {
  const analysis = await api.analyze('BTCUSDT');
} catch (error) {
  if (error.status === 401) {
    // Перенаправить на авторизацию
    redirectToAuth();
  } else if (error.status === 429) {
    // Показать сообщение о лимите
    showRateLimitMessage();
  } else {
    // Общая обработка ошибок
    showErrorMessage(error.message);
  }
}
```

## Performance Optimization

### Кэширование
- Результаты анализа кэшируются на 5 минут
- OHLCV данные кэшируются на 1 минуту
- Используйте заголовки `Cache-Control` для оптимизации

### Rate Limiting
- 100 запросов в минуту для авторизованных пользователей
- 10 запросов в минуту для неавторизованных
- Анализ: максимум 10 запросов в час

## Support & Documentation

### Дополнительные ресурсы
- [TradingView Charts Documentation](https://tradingview.github.io/lightweight-charts/)
- [Telegram WebApp API](https://core.telegram.org/bots/webapps)
- [Oracle Cloud Documentation](https://docs.oracle.com/en-us/iaas/)

### Контакты
- Telegram: @your_support_bot
- Email: support@chartgenius.online
- GitHub Issues: https://github.com/2511319/chartgenius-v3/issues

---

**Версия документа**: 1.0  
**Дата обновления**: 2025-01-16  
**Совместимость**: ChartGenius v3.0+
