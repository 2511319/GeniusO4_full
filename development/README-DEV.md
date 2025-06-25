# 🚀 ChartGenius - Среда Разработки

**Версия:** 1.1.0-dev  
**Окружение:** Development  
**Дата создания:** 25.06.2025

## ⚠️ ВАЖНЫЕ ПРАВИЛА

### 🔒 ЗАПРЕЩЕНО:
- ❌ Изменять файлы в `/production/`
- ❌ Пушить в ветку `ChartGenius-prod-try`
- ❌ Использовать продакшен-конфигурации
- ❌ Изменять продакшен-порты (3000, 8000)

### ✅ РАЗРЕШЕНО:
- ✅ Экспериментировать с кодом в `/development/`
- ✅ Создавать feature-ветки от `development`
- ✅ Тестировать на localhost:3001
- ✅ Изменять dev-конфигурации

## 🏗️ Структура Проекта

```
D:/project/GeniusO4_esc/
├── production/                    # 🔒 СТАБИЛЬНАЯ ПРОДАКШЕН-ВЕРСИЯ
│   ├── frontend/                  # Версия 1.0.51 (НЕ ТРОГАТЬ!)
│   ├── backend/
│   └── bot/
├── development/                   # 🚀 СРЕДА РАЗРАБОТКИ
│   ├── frontend-dev/              # Версия 1.1.0-dev
│   ├── backend-dev/
│   ├── bot-dev/
│   ├── .env.development
│   ├── docker-compose.dev.yml
│   └── README-DEV.md (этот файл)
```

## 🚀 Быстрый Старт

### 1. Первоначальная настройка
```bash
# Переключиться на ветку разработки
git checkout development

# Перейти в директорию разработки
cd development

# Настроить защитные механизмы
bash setup-git-hooks.sh

# Установить зависимости фронтенда
cd frontend-dev
npm install
cd ..
```

### 2. Запуск dev-окружения

#### Вариант A: Docker Compose (рекомендуется)
```bash
# Запуск всех сервисов
docker-compose -f docker-compose.dev.yml up -d

# Просмотр логов
docker-compose -f docker-compose.dev.yml logs -f

# Остановка
docker-compose -f docker-compose.dev.yml down
```

#### Вариант B: Локальный запуск
```bash
# Фронтенд (терминал 1)
cd frontend-dev
npm run dev
# Доступен на http://localhost:3001

# Бэкенд (терминал 2)
cd backend-dev
python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload

# Бот (терминал 3)
cd bot-dev
python bot.py
```

## 🔧 Конфигурация

### Порты разработки:
- **Frontend:** http://localhost:3001
- **Backend:** http://localhost:8001  
- **Bot:** http://localhost:8002

### Переменные окружения:
- Файл: `.env.development`
- Версия: `1.1.0-dev`
- Режим: `development`

## 🔄 Workflow Разработки

### Создание новой функции:
```bash
# 1. Убедиться что на ветке development
git checkout development
git pull origin development

# 2. Создать feature-ветку
git checkout -b feature/new-awesome-feature

# 3. Разработка
cd development/frontend-dev
npm run dev
# Вносить изменения...

# 4. Тестирование
npm run test
npm run build:dev

# 5. Коммит и пуш
git add .
git commit -m "feat: добавлена новая крутая функция"
git push origin feature/new-awesome-feature

# 6. Мерж в development (НЕ в продакшен!)
git checkout development
git merge feature/new-awesome-feature
```

## 🧪 Тестирование

```bash
# Фронтенд тесты
cd frontend-dev
npm run test

# Сборка для разработки
npm run build:dev

# Сборка для staging
npm run build:staging
```

## 📊 Мониторинг

### Логи:
```bash
# Docker логи
docker-compose -f docker-compose.dev.yml logs -f frontend-dev
docker-compose -f docker-compose.dev.yml logs -f backend-dev

# Файлы логов
tail -f logs/development.log
```

### Статус сервисов:
```bash
# Docker статус
docker-compose -f docker-compose.dev.yml ps

# Проверка портов
netstat -an | findstr "3001 8001 8002"
```

## 🔒 Безопасность

### Установленные защиты:
- ✅ Git hooks блокируют пуш в продакшен
- ✅ Автоматическая проверка изменений
- ✅ Изоляция портов и конфигураций
- ✅ Отдельная сеть Docker

### При возникновении ошибок:
```bash
# Если случайно попали в продакшен-ветку
git checkout development

# Если изменили файлы продакшена
git reset HEAD production/
git checkout -- production/

# Сброс к чистому состоянию
git stash
git checkout development
git pull origin development
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте текущую ветку: `git branch --show-current`
2. Убедитесь что в директории `development/`
3. Проверьте порты: `netstat -an | findstr "3001"`
4. Перезапустите dev-окружение

---

**🎯 Цель:** Безопасная разработка с полной изоляцией от продакшена  
**📋 Статус:** Готово к использованию  
**🔄 Последнее обновление:** 25.06.2025
