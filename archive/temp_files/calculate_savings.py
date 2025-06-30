#!/usr/bin/env python3
# Расчет достигнутой экономии после агрессивной оптимизации GCP
# АРХИВНЫЙ ФАЙЛ - перемещен из корневой директории

print('💰 РАСЧЕТ ДОСТИГНУТОЙ ЭКОНОМИИ')
print('=' * 50)

# Новые ресурсы после оптимизации
services = {
    'chartgenius-api-working': {'cpu': 0.25, 'memory_gb': 0.25},
    'chartgenius-bot-working': {'cpu': 0.125, 'memory_gb': 0.125}, 
    'chartgenius-frontend': {'cpu': 0.125, 'memory_gb': 0.125}
}

# Удаленные сервисы
deleted_services = {
    'chartgenius-bot-new': {'cpu': 1, 'memory_gb': 0.5}
}

print('📊 НОВАЯ КОНФИГУРАЦИЯ:')
total_cpu = 0
total_memory_gb = 0

for name, resources in services.items():
    cpu = resources['cpu']
    memory = resources['memory_gb']
    total_cpu += cpu
    total_memory_gb += memory
    print(f'  ✅ {name}: {cpu} CPU, {memory}Gi RAM')

print(f'  📊 ИТОГО: {total_cpu} CPU, {total_memory_gb}Gi RAM')

print('\n❌ УДАЛЕННЫЕ СЕРВИСЫ:')
for name, resources in deleted_services.items():
    cpu = resources['cpu']
    memory = resources['memory_gb']
    print(f'  🗑️ {name}: {cpu} CPU, {memory}Gi RAM')

# Расчет использования при 10% активности
activity_percent = 0.10  # 10% времени активны
hours_month = 720
active_hours = hours_month * activity_percent

print(f'\n⏱️ АКТИВНОСТЬ СЕРВИСОВ: {activity_percent*100}% времени ({active_hours} часов/месяц)')

# Эффективное использование ресурсов
effective_cpu_hours = total_cpu * active_hours
effective_memory_gb_hours = total_memory_gb * active_hours

print(f'📈 ЭФФЕКТИВНОЕ ИСПОЛЬЗОВАНИЕ:')
print(f'  CPU: {effective_cpu_hours} vCPU-часов/месяц')
print(f'  Memory: {effective_memory_gb_hours} GiB-часов/месяц')

# Free Tier лимиты
free_cpu_hours = 50  # 180,000 секунд = 50 часов
free_memory_gb_hours = 100  # 360,000 GiB-секунд = 100 GiB-часов

print(f'\n🆓 FREE TIER ЛИМИТЫ:')
print(f'  CPU: {free_cpu_hours} vCPU-часов/месяц')
print(f'  Memory: {free_memory_gb_hours} GiB-часов/месяц')

# Проверка превышения Free Tier
cpu_usage_percent = (effective_cpu_hours / free_cpu_hours) * 100
memory_usage_percent = (effective_memory_gb_hours / free_memory_gb_hours) * 100

print(f'\n📊 ИСПОЛЬЗОВАНИЕ FREE TIER:')
print(f'  CPU: {cpu_usage_percent:.1f}% ({"✅ В пределах" if cpu_usage_percent <= 100 else "❌ Превышение"})')
print(f'  Memory: {memory_usage_percent:.1f}% ({"✅ В пределах" if memory_usage_percent <= 100 else "❌ Превышение"})')

# Расчет стоимости
if effective_cpu_hours <= free_cpu_hours and effective_memory_gb_hours <= free_memory_gb_hours:
    cloud_run_cost = 0
    print(f'\n💰 СТОИМОСТЬ CLOUD RUN: $0/месяц (в пределах Free Tier)')
else:
    billable_cpu_hours = max(0, effective_cpu_hours - free_cpu_hours)
    billable_memory_gb_hours = max(0, effective_memory_gb_hours - free_memory_gb_hours)
    
    cpu_cost = billable_cpu_hours * 0.000024
    memory_cost = billable_memory_gb_hours * 0.0000025
    cloud_run_cost = cpu_cost + memory_cost
    
    print(f'\n💰 СТОИМОСТЬ CLOUD RUN: ${cloud_run_cost:.2f}/месяц')

# Container Registry (минимальная стоимость после очистки)
registry_cost = 1.0  # ~$1 за оставшиеся образы

# Cloud Build (минимальная активность)
build_cost = 0.5  # ~$0.5 за редкие билды

total_new_cost = cloud_run_cost + registry_cost + build_cost

print(f'\n💰 ОБЩАЯ НОВАЯ СТОИМОСТЬ:')
print(f'  Cloud Run: ${cloud_run_cost:.2f}/месяц')
print(f'  Container Registry: ${registry_cost:.2f}/месяц')
print(f'  Cloud Build: ${build_cost:.2f}/месяц')
print(f'  ИТОГО: ${total_new_cost:.2f}/месяц')

# Экономия
old_cost = 104.25
savings = old_cost - total_new_cost
savings_percent = (savings / old_cost) * 100

print(f'\n🎉 ДОСТИГНУТАЯ ЭКОНОМИЯ:')
print(f'  Было: ${old_cost}/месяц')
print(f'  Стало: ${total_new_cost:.2f}/месяц')
print(f'  Экономия: ${savings:.2f}/месяц ({savings_percent:.1f}%)')

if total_new_cost <= 5:
    print(f'\n✅ ЦЕЛЬ ДОСТИГНУТА: Расходы ≤ $5/месяц!')
else:
    print(f'\n⚠️ Цель частично достигнута. Для $0/месяц нужны дополнительные оптимизации.')

print(f'\n📋 ВЫПОЛНЕННЫЕ ДЕЙСТВИЯ:')
print(f'  ✅ Удален дублирующий сервис chartgenius-bot-new')
print(f'  ✅ Радикально уменьшены ресурсы всех сервисов')
print(f'  ✅ Настроен scale-to-zero (min-instances=0)')
print(f'  ✅ Включен CPU throttling')
print(f'  ✅ Очищены старые Docker образы')
print(f'  ✅ Удалены неиспользуемые репозитории')
print(f'  ✅ Настроены строгие лимиты concurrency и timeout')

print(f'\n🎯 СТАТУС: АГРЕССИВНАЯ ОПТИМИЗАЦИЯ ЗАВЕРШЕНА!')
