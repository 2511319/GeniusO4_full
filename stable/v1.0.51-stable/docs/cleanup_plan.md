# 🧹 ПЛАН ОЧИСТКИ И ОРГАНИЗАЦИИ ПРОЕКТА CHARTGENIUS

**Дата:** 25.06.2025  
**Версия:** v1.0.51-stable  
**Статус:** Готов к выполнению  

---

## 📋 ТЕКУЩЕЕ СОСТОЯНИЕ ДИРЕКТОРИИ

### Файлы для архивирования:
```
Временные файлы:
├── current_api_config.yaml
├── test_bot_quick.py
├── calculate_savings.py
├── bot_deployment_test_results.json (если существует)
└── *.log файлы

Скрипты оптимизации:
├── gcp_cost_optimization_scripts.sh
├── emergency_cost_optimization.sh
├── gcp_cost_monitor.py
├── aggressive_optimization_report.md
└── gcp_cost_analysis_june_2025.md

Тестовые файлы:
├── production/test-bot-deployment.py
├── production/quick-bot-check.py
└── Любые временные тестовые скрипты
```

---

## 🗂️ ЦЕЛЕВАЯ СТРУКТУРА ДИРЕКТОРИЙ

```
chartgenius/
├── production/                    # Стабильная продакшн-версия
│   ├── VERSION                    # v1.0.51
│   ├── backend/
│   ├── frontend/
│   ├── bot/
│   └── docker-compose.yml
│
├── development/                   # Разработка (изолированная)
│   ├── VERSION                    # v1.1.0-dev
│   ├── backend-dev/
│   ├── frontend-dev/
│   ├── bot-dev/
│   └── Chartgenius_r_tr.md
│
├── stable/                        # Стабильные версии для rollback
│   └── v1.0.51-stable/
│       ├── README.md
│       ├── cloud_run_configs/
│       ├── scripts/
│       └── docs/
│
├── scripts/                       # Утилиты и скрипты
│   ├── maintenance/
│   ├── deployment/
│   └── monitoring/
│
├── docs/                          # Документация
│   ├── optimization/
│   ├── deployment/
│   └── troubleshooting/
│
└── archive/                       # Архив временных файлов
    ├── temp_files/
    ├── optimization_scripts/
    └── test_files/
```

---

## 🧹 ПЛАН ОЧИСТКИ

### **Phase 1: Архивирование временных файлов**

#### Файлы для перемещения в `archive/temp_files/`:
```bash
# Временные конфигурации
mv current_api_config.yaml archive/temp_files/
mv *.log archive/temp_files/ 2>/dev/null || true

# Тестовые Python скрипты
mv test_bot_quick.py archive/temp_files/
mv calculate_savings.py archive/temp_files/
```

#### Файлы для перемещения в `archive/optimization_scripts/`:
```bash
# Скрипты оптимизации
mv gcp_cost_optimization_scripts.sh archive/optimization_scripts/
mv emergency_cost_optimization.sh archive/optimization_scripts/
mv gcp_cost_monitor.py archive/optimization_scripts/

# Отчеты об оптимизации
mv aggressive_optimization_report.md archive/optimization_scripts/
mv gcp_cost_analysis_june_2025.md archive/optimization_scripts/
```

#### Файлы для перемещения в `archive/test_files/`:
```bash
# Тестовые скрипты
mv production/test-bot-deployment.py archive/test_files/
mv production/quick-bot-check.py archive/test_files/
```

### **Phase 2: Организация документации**

#### Создать `docs/optimization/`:
```bash
# Переместить документацию по оптимизации
mv archive/optimization_scripts/*.md docs/optimization/

# Создать индексный файл
echo "# Документация по оптимизации" > docs/optimization/README.md
```

#### Создать `docs/deployment/`:
```bash
# Документация по развертыванию
cp stable/v1.0.51-stable/README.md docs/deployment/stable_version.md
```

### **Phase 3: Организация скриптов**

#### Создать `scripts/maintenance/`:
```bash
# Скрипты обслуживания
cp stable/v1.0.51-stable/scripts/*.sh scripts/maintenance/
```

#### Создать `scripts/monitoring/`:
```bash
# Скрипты мониторинга
mv archive/optimization_scripts/gcp_cost_monitor.py scripts/monitoring/
```

---

## 🔄 КОМАНДЫ ДЛЯ ВЫПОЛНЕНИЯ

### **Создание структуры директорий:**
```bash
# Основные директории
mkdir -p archive/temp_files
mkdir -p archive/optimization_scripts  
mkdir -p archive/test_files
mkdir -p docs/optimization
mkdir -p docs/deployment
mkdir -p docs/troubleshooting
mkdir -p scripts/maintenance
mkdir -p scripts/deployment
mkdir -p scripts/monitoring
```

### **Перемещение файлов:**
```bash
# Временные файлы
mv current_api_config.yaml archive/temp_files/ 2>/dev/null || true
mv test_bot_quick.py archive/temp_files/ 2>/dev/null || true
mv calculate_savings.py archive/temp_files/ 2>/dev/null || true
mv *.log archive/temp_files/ 2>/dev/null || true

# Скрипты оптимизации
mv gcp_cost_optimization_scripts.sh archive/optimization_scripts/ 2>/dev/null || true
mv emergency_cost_optimization.sh archive/optimization_scripts/ 2>/dev/null || true
mv gcp_cost_monitor.py archive/optimization_scripts/ 2>/dev/null || true

# Отчеты
mv aggressive_optimization_report.md archive/optimization_scripts/ 2>/dev/null || true
mv gcp_cost_analysis_june_2025.md archive/optimization_scripts/ 2>/dev/null || true

# Тестовые файлы
mv production/test-bot-deployment.py archive/test_files/ 2>/dev/null || true
mv production/quick-bot-check.py archive/test_files/ 2>/dev/null || true
```

### **Копирование в целевые директории:**
```bash
# Документация
cp archive/optimization_scripts/*.md docs/optimization/ 2>/dev/null || true

# Скрипты
cp stable/v1.0.51-stable/scripts/*.sh scripts/maintenance/ 2>/dev/null || true
cp archive/optimization_scripts/gcp_cost_monitor.py scripts/monitoring/ 2>/dev/null || true
```

---

## 📝 ФАЙЛЫ ДЛЯ УДАЛЕНИЯ

### **Безопасно удаляемые файлы:**
```bash
# Временные файлы после архивирования
rm -f current_api_config.yaml
rm -f test_bot_quick.py  
rm -f calculate_savings.py
rm -f *.log

# Дублирующие скрипты после архивирования
rm -f gcp_cost_optimization_scripts.sh
rm -f emergency_cost_optimization.sh
rm -f gcp_cost_monitor.py
```

### **⚠️ НЕ УДАЛЯТЬ:**
- Любые файлы в `production/`
- Любые файлы в `development/`
- Конфигурационные файлы (.env, docker-compose.yml)
- Исходный код приложений

---

## ✅ ПРОВЕРОЧНЫЙ СПИСОК

### После выполнения очистки:
- [ ] Все временные файлы перемещены в `archive/`
- [ ] Скрипты оптимизации архивированы
- [ ] Документация организована в `docs/`
- [ ] Утилиты перемещены в `scripts/`
- [ ] Продакшн-файлы не затронуты
- [ ] Development-файлы не затронуты
- [ ] Стабильная версия сохранена в `stable/`

### Проверка работоспособности:
- [ ] Продакшн-сервисы работают
- [ ] Telegram bot отвечает
- [ ] WebApp доступен
- [ ] Скрипты rollback функциональны

---

## 📞 КОНТАКТЫ

При проблемах с очисткой:
- Проверить `stable/v1.0.51-stable/` для восстановления
- Использовать `emergency_rollback.sh` при критических проблемах
- Обратиться к документации в `docs/`

**Статус:** Готов к выполнению  
**Приоритет:** Средний (после стабилизации системы)
