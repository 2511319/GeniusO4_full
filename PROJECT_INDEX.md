# 🚀 ChartGenius Project Index

**Версия:** v1.0.51-stable  
**Дата обновления:** 25.06.2025  
**Статус:** ✅ Готов к продакшену  

---

## 📋 БЫСТРАЯ НАВИГАЦИЯ

### **🔥 Критические действия:**
- **Экстренный rollback:** `stable/v1.0.51-stable/scripts/emergency_rollback.sh`
- **Полное восстановление:** `stable/v1.0.51-stable/scripts/restore_stable_version.sh`
- **Мониторинг расходов:** `gcp_cost_monitor.py`

### **📊 Текущий статус:**
- **Расходы:** $1.50/месяц (98.6% экономии)
- **Сервисы:** 3 активных (оптимизированы)
- **Free Tier:** ✅ В пределах лимитов
- **Telegram Bot:** ✅ Работает

---

## 🗂️ СТРУКТУРА ПРОЕКТА

### **📁 Основные директории:**

#### **production/** - Стабильная продакшн-версия
```
production/
├── VERSION (v1.0.51)
├── backend/
├── frontend/
├── bot/
└── docker-compose.yml
```
**Статус:** ✅ Стабильно работает, НЕ ИЗМЕНЯТЬ

#### **development/** - Изолированная разработка
```
development/
├── VERSION (v1.1.0-dev)
├── backend-dev/
├── frontend-dev/
├── bot-dev/
└── Chartgenius_r_tr.md
```
**Статус:** 🔄 В разработке, изолированная среда

#### **stable/** - Версии для rollback
```
stable/v1.0.51-stable/
├── README.md
├── CHANGELOG.md
├── cloud_run_configs/stable_config.yaml
├── scripts/restore_stable_version.sh
├── scripts/emergency_rollback.sh
└── docs/cleanup_plan.md
```
**Статус:** 🔒 Защищенная версия для восстановления

---

## 🔧 БЫСТРЫЕ КОМАНДЫ

### **Восстановление системы:**
```bash
# Полное восстановление стабильной версии
cd stable/v1.0.51-stable/scripts/
./restore_stable_version.sh

# Экстренный rollback (без подтверждений)
./emergency_rollback.sh
```

### **Мониторинг:**
```bash
# Проверка статуса сервисов
gcloud run services list --region=europe-west1

# Мониторинг расходов
python gcp_cost_monitor.py

# Проверка Telegram bot
curl https://api.telegram.org/bot7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0/getWebhookInfo
```

### **Организация проекта:**
```bash
# Автоматическая организация файлов
python organize_project.py

# Ручная организация (см. cleanup_plan.md)
```

---

## 📊 ТЕКУЩАЯ КОНФИГУРАЦИЯ

### **Cloud Run Services:**
| Сервис | CPU | Memory | Status |
|--------|-----|--------|--------|
| chartgenius-api-working | 0.25 | 256Mi | ✅ Active |
| chartgenius-bot-working | 0.125 | 128Mi | ✅ Active |
| chartgenius-frontend | 0.125 | 128Mi | ✅ Active |

### **Экономические показатели:**
- **Месячные расходы:** $1.50 (было $104.25)
- **Экономия:** 98.6%
- **Budget alerts:** $5/месяц
- **Free Tier статус:** ✅ В пределах лимитов

---

## 📚 ДОКУМЕНТАЦИЯ

### **Основная документация:**
- [`stable/v1.0.51-stable/README.md`](stable/v1.0.51-stable/README.md) - Описание стабильной версии
- [`stable/v1.0.51-stable/CHANGELOG.md`](stable/v1.0.51-stable/CHANGELOG.md) - Детальные изменения
- [`stable/v1.0.51-stable/docs/cleanup_plan.md`](stable/v1.0.51-stable/docs/cleanup_plan.md) - План организации

### **Отчеты:**
- [`organization_execution_report.md`](organization_execution_report.md) - Отчет о выполнении организации
- [`final_organization_report.md`](final_organization_report.md) - Финальный отчет
- [`aggressive_optimization_report.md`](aggressive_optimization_report.md) - Отчет об оптимизации

### **Технические спецификации:**
- [`development/Chartgenius_r_tr.md`](development/Chartgenius_r_tr.md) - Техническое задание v1.1.0-dev
- [`stable/v1.0.51-stable/cloud_run_configs/stable_config.yaml`](stable/v1.0.51-stable/cloud_run_configs/stable_config.yaml) - Конфигурация сервисов

---

## 🔄 ПРОЦЕДУРЫ ROLLBACK

### **Когда использовать:**
- 🚨 **Emergency rollback:** Критические проблемы, система не работает
- 🔧 **Full restore:** Проблемы с производительностью, нужно восстановление с backup

### **Время выполнения:**
- **Emergency rollback:** <2 минуты
- **Full restore:** 5-10 минут (с проверками)

### **Что восстанавливается:**
- Конфигурация всех Cloud Run сервисов
- Настройки scaling и performance
- Webhook конфигурация Telegram bot
- Environment variables

---

## 📈 ПЛАН РАЗВИТИЯ

### **v1.0.51-stable (Текущая):**
- ✅ Агрессивная оптимизация расходов
- ✅ Scale-to-zero конфигурация
- ✅ Автоматизированные rollback процедуры
- ✅ Comprehensive documentation

### **v1.1.0-dev (В разработке):**
- 🔄 Event-driven архитектура (Celery + Redis)
- 🔄 Hybrid admin panel (Grafana + Custom UI)
- 🔄 Миграция на aiogram
- 🔄 CCXT интеграция
- 🔄 Dynamic indicators система

### **v1.2.0 (Планируется):**
- 📋 Автоматическое масштабирование
- 📋 Advanced analytics
- 📋 Multi-region deployment
- 📋 Enhanced security

---

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

### **Безопасность:**
- **НЕ ИЗМЕНЯТЬ** файлы в `production/` без rollback плана
- **ВСЕГДА** тестировать изменения в `development/`
- **ИСПОЛЬЗОВАТЬ** rollback при любых проблемах

### **Мониторинг:**
- **Ежедневно:** Проверять budget alerts
- **Еженедельно:** Анализировать производительность
- **При проблемах:** Использовать rollback процедуры

### **Производительность:**
- **Cold start:** 2-5 секунд (нормально для scale-to-zero)
- **Warm response:** <500ms
- **Concurrency:** Ограничено 1 запросом одновременно

---

## 📞 ПОДДЕРЖКА

### **Экстренные ситуации:**
1. **Система не работает:** `emergency_rollback.sh`
2. **Проблемы с производительностью:** `restore_stable_version.sh`
3. **Превышение бюджета:** Проверить budget alerts, оптимизировать ресурсы

### **Контакты:**
- **Техническая документация:** `stable/v1.0.51-stable/`
- **Планы развития:** `development/Chartgenius_r_tr.md`
- **Отчеты:** `*_report.md` файлы

---

## 🎯 СТАТУС ПРОЕКТА

**✅ ChartGenius v1.0.51-stable готов к продакшену!**

- 🔒 **Стабильность:** Все сервисы работают корректно
- 💰 **Экономичность:** 98.6% экономии расходов
- 🔄 **Надежность:** Автоматизированные rollback процедуры
- 📚 **Документированность:** Полная техническая документация
- 🚀 **Масштабируемость:** Готовность к развитию v1.1.0-dev

**Следующий этап:** Развитие новых возможностей в изолированной среде `development/`

---

**Дата последнего обновления:** 25.06.2025  
**Ответственный:** Technical Team  
**Статус:** ✅ Production Ready
