#!/bin/bash
# 🔒 Настройка защитных Git hooks для безопасной разработки

echo "🔒 Настройка защитных механизмов Git..."

# Создаем директорию для hooks если её нет
mkdir -p ../.git/hooks

# Создаем pre-push hook для защиты продакшена
cat > ../.git/hooks/pre-push << 'EOF'
#!/bin/bash
# 🔒 ЗАЩИТА ПРОДАКШЕНА - Запрет пуша в продакшен-ветку

current_branch=$(git branch --show-current)

if [[ "$current_branch" == "ChartGenius-prod-try" ]]; then
    echo "❌ ЗАПРЕЩЕНО: Пуш в продакшен-ветку заблокирован!"
    echo "🚀 Используйте ветку 'development' для разработки"
    echo "📋 Текущая ветка: $current_branch"
    echo ""
    echo "Для переключения на ветку разработки:"
    echo "git checkout development"
    exit 1
fi

if [[ "$current_branch" == "master1" ]]; then
    echo "❌ ЗАПРЕЩЕНО: Пуш в основную ветку заблокирован!"
    echo "🚀 Используйте ветку 'development' для разработки"
    exit 1
fi

echo "✅ Пуш разрешен для ветки: $current_branch"
EOF

# Создаем pre-commit hook для проверки изменений
cat > ../.git/hooks/pre-commit << 'EOF'
#!/bin/bash
# 🔒 ЗАЩИТА ПРОДАКШЕНА - Проверка изменений

# Проверяем, не изменяются ли файлы продакшена
if git diff --cached --name-only | grep -q "^production/"; then
    echo "❌ ЗАПРЕЩЕНО: Обнаружены изменения в директории production/"
    echo "🔒 Продакшен-версия должна оставаться нетронутой!"
    echo ""
    echo "Измененные файлы продакшена:"
    git diff --cached --name-only | grep "^production/" | sed 's/^/  - /'
    echo ""
    echo "Отмените изменения командой:"
    echo "git reset HEAD production/"
    exit 1
fi

echo "✅ Коммит безопасен - изменения только в development/"
EOF

# Делаем hooks исполняемыми
chmod +x ../.git/hooks/pre-push
chmod +x ../.git/hooks/pre-commit

echo "✅ Защитные механизмы настроены!"
echo ""
echo "🔒 Установленные защиты:"
echo "  - Запрет пуша в продакшен-ветки"
echo "  - Запрет изменения файлов production/"
echo "  - Автоматическая проверка при коммитах"
echo ""
echo "🚀 Теперь можно безопасно разрабатывать в development/"
