# 🔧 ПЛАН ИСПРАВЛЕНИЙ ДЛЯ ПРОДАКШЕНА
## ChartGenius - Детальные инструкции

---

## 🚨 ЭТАП 1: КРИТИЧЕСКИЕ ИСПРАВЛЕНИЯ (30 минут)

### 1.1 Унификация API URL

**Проблема:** Разные URL в продакшн файлах

**Исправления:**

```bash
# 1. Обновить production/frontend/nginx.conf
sed -i 's|chartgenius-api-europe-west1-a.run.app|chartgenius-api-169129692197.europe-west1.run.app|g' production/frontend/nginx.conf

# 2. Обновить production/frontend/Dockerfile
sed -i 's|chartgenius-api-europe-west1-a.run.app|chartgenius-api-169129692197.europe-west1.run.app|g' production/frontend/Dockerfile
```

### 1.2 Синхронизация версий

**Текущие версии:**
- production/VERSION: 1.0.0
- production/frontend/src/config.js: 1.0.2
- frontend/package.json: 0.1.0

**Решение - установить единую версию 1.0.2:**

```bash
# Обновить production/VERSION
echo "1.0.2" > production/VERSION

# Обновить frontend/package.json
sed -i 's/"version": "0.1.0"/"version": "1.0.2"/' frontend/package.json

# Обновить production/backend/app.py
sed -i 's/version="1.0.0"/version="1.0.2"/' production/backend/app.py
```

### 1.3 Удаление хардкод localhost

**Файл:** `production/frontend/vite.config.js`

```javascript
// ЗАМЕНИТЬ строку 33:
target: process.env.VITE_API_URL || 'http://localhost:8080',
// НА:
target: process.env.VITE_API_URL || 'https://chartgenius-api-169129692197.europe-west1.run.app',
```

### 1.4 Удаление реального токена

**Файл:** `production/setup-secrets.ps1`

```powershell
# ЗАМЕНИТЬ строку 36:
default = "7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0"
# НА:
default = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
```

---

## ⚡ ЭТАП 2: ВЫСОКИЙ ПРИОРИТЕТ (1 час)

### 2.1 Создание config.js для development

**Создать файл:** `frontend/src/config.js`

```javascript
// frontend/src/config.js
// Конфигурация для development версии

// API URL - для development используем относительные пути
export const API_URL = '';

// Версия приложения
export const APP_VERSION = '1.0.2';

// Режим отладки
export const DEBUG = true;

// Конфигурация для API запросов
export const API_CONFIG = {
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
};

console.log('Development Config:', {
  API_URL: API_URL || 'relative paths',
  APP_VERSION,
  DEBUG
});
```

### 2.2 Добавление версионирования в UI

**Создать компонент:** `frontend/src/components/VersionInfo.jsx`

```jsx
import React from 'react';
import { Box, Typography, Chip } from '@mui/material';
import { APP_VERSION, DEBUG } from '../config';

export default function VersionInfo() {
  return (
    <Box sx={{ 
      position: 'fixed', 
      bottom: 8, 
      right: 8, 
      zIndex: 1000,
      display: 'flex',
      gap: 1
    }}>
      <Chip 
        label={`v${APP_VERSION}`} 
        size="small" 
        color="primary" 
        variant="outlined"
      />
      {DEBUG && (
        <Chip 
          label="DEV" 
          size="small" 
          color="warning" 
          variant="filled"
        />
      )}
    </Box>
  );
}
```

**Добавить в App.jsx:**

```jsx
// В frontend/src/App.jsx добавить импорт:
import VersionInfo from './components/VersionInfo';

// В return добавить перед закрывающим </>:
<VersionInfo />
```

### 2.3 Синхронизация CORS настроек

**Обновить:** `backend/app.py`

```python
# ЗАМЕНИТЬ строки 30-33:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# НА:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Development frontend
        "http://localhost:3000",  # Alternative dev port
        "https://t.me",           # Telegram WebApp
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### 2.4 Удаление console.log из продакшн

**Файл:** `production/frontend/src/config.js`

```javascript
// ЗАМЕНИТЬ строки 22-26:
console.log('Frontend Config:', {
  API_URL,
  APP_VERSION,
  DEBUG
});

// НА:
if (DEBUG) {
  console.log('Frontend Config:', {
    API_URL,
    APP_VERSION,
    DEBUG
  });
}
```

---

## 🔄 ЭТАП 3: УЛУЧШЕНИЯ (2 часа)

### 3.1 Создание скрипта проверки конфигурации

**Создать файл:** `scripts/check-config.sh`

```bash
#!/bin/bash
# Скрипт проверки соответствия конфигураций

echo "🔍 Проверка конфигурации ChartGenius..."

# Проверка версий
PROD_VERSION=$(cat production/VERSION)
FRONTEND_VERSION=$(grep '"version"' frontend/package.json | cut -d'"' -f4)
CONFIG_VERSION=$(grep 'APP_VERSION' production/frontend/src/config.js | cut -d"'" -f2)

echo "📊 Версии:"
echo "  Production: $PROD_VERSION"
echo "  Frontend: $FRONTEND_VERSION"
echo "  Config: $CONFIG_VERSION"

if [ "$PROD_VERSION" = "$FRONTEND_VERSION" ] && [ "$PROD_VERSION" = "$CONFIG_VERSION" ]; then
    echo "✅ Версии синхронизированы"
else
    echo "❌ Версии не синхронизированы!"
    exit 1
fi

# Проверка API URL
echo "🔗 Проверка API URL..."
grep -r "localhost" production/ && echo "❌ Найден localhost в продакшн файлах!" || echo "✅ localhost не найден в продакшн"

echo "✅ Проверка завершена"
```

### 3.2 Создание интерфейса статуса сервисов

**Создать компонент:** `frontend/src/components/ServiceStatus.jsx`

```jsx
import React, { useState, useEffect } from 'react';
import { 
  Dialog, DialogTitle, DialogContent, 
  List, ListItem, ListItemText, 
  Chip, IconButton, Box 
} from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import { API_URL, APP_VERSION } from '../config';

export default function ServiceStatus() {
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState({});

  const checkHealth = async () => {
    try {
      const response = await fetch(`${API_URL}/health`);
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      setStatus({ error: error.message });
    }
  };

  useEffect(() => {
    if (open) checkHealth();
  }, [open]);

  return (
    <>
      <IconButton 
        onClick={() => setOpen(true)}
        sx={{ position: 'fixed', bottom: 8, left: 8 }}
      >
        <InfoIcon />
      </IconButton>
      
      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>Статус сервисов</DialogTitle>
        <DialogContent>
          <List>
            <ListItem>
              <ListItemText 
                primary="Frontend версия" 
                secondary={APP_VERSION}
              />
              <Chip label="OK" color="success" size="small" />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="API статус" 
                secondary={status.status || 'Проверка...'}
              />
              <Chip 
                label={status.status === 'healthy' ? 'OK' : 'ERROR'} 
                color={status.status === 'healthy' ? 'success' : 'error'} 
                size="small" 
              />
            </ListItem>
            {status.version && (
              <ListItem>
                <ListItemText 
                  primary="API версия" 
                  secondary={status.version}
                />
              </ListItem>
            )}
          </List>
        </DialogContent>
      </Dialog>
    </>
  );
}
```

---

## ✅ ПРОВЕРОЧНЫЙ ЧЕКЛИСТ

После выполнения всех исправлений проверить:

- [ ] Все API URL унифицированы
- [ ] Версии синхронизированы во всех файлах  
- [ ] Localhost удален из продакшн конфигов
- [ ] Реальные токены удалены из скриптов
- [ ] CORS настройки корректны
- [ ] Console.log удалены из продакшн
- [ ] Версионирование отображается в UI
- [ ] Скрипт проверки конфигурации работает

---

## 🚀 КОМАНДЫ ДЛЯ БЫСТРОГО ИСПРАВЛЕНИЯ

```bash
# Выполнить все критические исправления одной командой:
cd /path/to/project

# 1. Унификация API URL
sed -i 's|chartgenius-api-europe-west1-a.run.app|chartgenius-api-169129692197.europe-west1.run.app|g' production/frontend/nginx.conf production/frontend/Dockerfile

# 2. Синхронизация версий
echo "1.0.2" > production/VERSION
sed -i 's/"version": "0.1.0"/"version": "1.0.2"/' frontend/package.json
sed -i 's/version="1.0.0"/version="1.0.2"/' production/backend/app.py

# 3. Проверка результата
echo "✅ Критические исправления выполнены"
echo "📋 Проверьте файлы вручную для подтверждения изменений"
```
