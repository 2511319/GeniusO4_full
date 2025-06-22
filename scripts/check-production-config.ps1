# scripts/check-production-config.ps1
# Скрипт проверки готовности конфигурации к продакшену (PowerShell версия)

Write-Host "🔍 ПРОВЕРКА ГОТОВНОСТИ CHARTGENIUS К ПРОДАКШЕНУ" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

$Errors = 0
$Warnings = 0

function Write-Error-Custom($message) {
    Write-Host "❌ ОШИБКА: $message" -ForegroundColor Red
    $script:Errors++
}

function Write-Warning-Custom($message) {
    Write-Host "⚠️  ПРЕДУПРЕЖДЕНИЕ: $message" -ForegroundColor Yellow
    $script:Warnings++
}

function Write-Success($message) {
    Write-Host "✅ $message" -ForegroundColor Green
}

function Write-Info($message) {
    Write-Host "ℹ️  $message" -ForegroundColor Blue
}

# 1. Проверка версий
Write-Host "`n📊 ПРОВЕРКА ВЕРСИЙ" -ForegroundColor Blue
Write-Host "==================="

$ProdVersion = if (Test-Path "production/VERSION") { Get-Content "production/VERSION" -Raw | ForEach-Object { $_.Trim() } } else { "НЕ НАЙДЕН" }
$FrontendVersion = if (Test-Path "frontend/package.json") { 
    (Get-Content "frontend/package.json" | ConvertFrom-Json).version 
} else { "НЕ НАЙДЕН" }

$ConfigVersion = if (Test-Path "production/frontend/src/config.js") {
    $content = Get-Content "production/frontend/src/config.js" -Raw
    if ($content -match "APP_VERSION = '([^']+)'") { $matches[1] } else { "НЕ НАЙДЕН" }
} else { "ФАЙЛ НЕ НАЙДЕН" }

$DevConfigVersion = if (Test-Path "frontend/src/config.js") {
    $content = Get-Content "frontend/src/config.js" -Raw
    if ($content -match "APP_VERSION = '([^']+)'") { $matches[1] } else { "НЕ НАЙДЕН" }
} else { "ФАЙЛ НЕ НАЙДЕН" }

Write-Host "Production VERSION: $ProdVersion"
Write-Host "Frontend package.json: $FrontendVersion"
Write-Host "Production config.js: $ConfigVersion"
Write-Host "Development config.js: $DevConfigVersion"

if ($ProdVersion -eq $FrontendVersion -and $ProdVersion -eq $ConfigVersion) {
    Write-Success "Версии синхронизированы"
} else {
    Write-Error-Custom "Версии не синхронизированы между компонентами"
}

# 2. Проверка API URL
Write-Host "`n🔗 ПРОВЕРКА API URL" -ForegroundColor Blue
Write-Host "==================="

# Проверка на localhost в продакшн файлах
$LocalhostFound = $false
if (Test-Path "production") {
    Get-ChildItem -Path "production" -Recurse -File | ForEach-Object {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -match "localhost|127\.0\.0\.1") {
            Write-Host "Найден localhost в: $($_.FullName)" -ForegroundColor Red
            $LocalhostFound = $true
        }
    }
}

if ($LocalhostFound) {
    Write-Error-Custom "Найдены localhost/127.0.0.1 в продакшн файлах"
} else {
    Write-Success "localhost не найден в продакшн файлах"
}

# Проверка соответствия API URL в продакшн файлах
$NginxApiUrl = if (Test-Path "production/frontend/nginx.conf") {
    $content = Get-Content "production/frontend/nginx.conf" -Raw
    if ($content -match "https://[^;]+\.run\.app") { $matches[0] } else { "НЕ НАЙДЕН" }
} else { "ФАЙЛ НЕ НАЙДЕН" }

$DockerfileApiUrl = if (Test-Path "production/frontend/Dockerfile") {
    $content = Get-Content "production/frontend/Dockerfile" -Raw
    if ($content -match "https://[^`"]+\.run\.app") { $matches[0] } else { "НЕ НАЙДЕН" }
} else { "ФАЙЛ НЕ НАЙДЕН" }

$ConfigApiUrl = if (Test-Path "production/frontend/src/config.js") {
    $content = Get-Content "production/frontend/src/config.js" -Raw
    if ($content -match "https://[^']+\.run\.app") { $matches[0] } else { "НЕ НАЙДЕН" }
} else { "ФАЙЛ НЕ НАЙДЕН" }

Write-Host "Nginx API URL: $NginxApiUrl"
Write-Host "Dockerfile API URL: $DockerfileApiUrl"
Write-Host "Config API URL: $ConfigApiUrl"

if ($NginxApiUrl -eq $DockerfileApiUrl -and $NginxApiUrl -eq $ConfigApiUrl -and $NginxApiUrl -ne "НЕ НАЙДЕН") {
    Write-Success "API URL синхронизированы в продакшн файлах"
} else {
    Write-Error-Custom "API URL не синхронизированы между продакшн файлами"
}

# 3. Проверка секретов
Write-Host "`n🔐 ПРОВЕРКА СЕКРЕТОВ" -ForegroundColor Blue
Write-Host "==================="

# Проверка на реальные токены в коде
$RealKeysFound = $false
Get-ChildItem -Recurse -File -Exclude "*.md" | Where-Object { 
    $_.DirectoryName -notmatch "node_modules|\.git" 
} | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
    if ($content -match "sk-[a-zA-Z0-9]{20,}" -and $content -notmatch "your-|example") {
        Write-Host "Найден возможный реальный API ключ в: $($_.FullName)" -ForegroundColor Red
        $RealKeysFound = $true
    }
}

if ($RealKeysFound) {
    Write-Error-Custom "Найдены возможные реальные API ключи в коде"
} else {
    Write-Success "Реальные API ключи не найдены в коде"
}

# Проверка Telegram токена в setup-secrets.ps1
if (Test-Path "production/setup-secrets.ps1") {
    $content = Get-Content "production/setup-secrets.ps1" -Raw
    if ($content -match "REAL_TOKEN_PATTERN_REMOVED:") {
        Write-Error-Custom "Найден реальный Telegram токен в setup-secrets.ps1"
    } else {
        Write-Success "Реальный Telegram токен не найден в скриптах"
    }
}

# 4. Проверка режимов отладки
Write-Host "`n🐛 ПРОВЕРКА РЕЖИМОВ ОТЛАДКИ" -ForegroundColor Blue
Write-Host "============================="

# Проверка DEBUG в продакшн конфигурации
if (Test-Path "production/backend/config/production.py") {
    $content = Get-Content "production/backend/config/production.py" -Raw
    if ($content -match "DEBUG = False") {
        Write-Success "DEBUG отключен в продакшн backend"
    } else {
        Write-Error-Custom "DEBUG не отключен в продакшн backend"
    }
}

if (Test-Path "production/frontend/src/config.js") {
    $content = Get-Content "production/frontend/src/config.js" -Raw
    if ($content -match "DEBUG = false") {
        Write-Success "DEBUG отключен в продакшн frontend"
    } else {
        Write-Warning-Custom "DEBUG не отключен в продакшн frontend"
    }
}

# Проверка console.log в продакшн
$ConsoleLogFound = $false
if (Test-Path "production") {
    Get-ChildItem -Path "production" -Recurse -File -Include "*.js" | ForEach-Object {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -match "console\.log") {
            $ConsoleLogFound = $true
        }
    }
}

if ($ConsoleLogFound) {
    Write-Warning-Custom "Найдены console.log в продакшн файлах"
} else {
    Write-Success "console.log не найдены в продакшн файлах"
}

# 5. Проверка Docker файлов
Write-Host "`n🐳 ПРОВЕРКА DOCKER КОНФИГУРАЦИИ" -ForegroundColor Blue
Write-Host "================================="

$DockerFiles = @("production/backend/Dockerfile", "production/frontend/Dockerfile", "production/bot/Dockerfile")

foreach ($dockerfile in $DockerFiles) {
    if (Test-Path $dockerfile) {
        Write-Success "Найден $dockerfile"
        
        $content = Get-Content $dockerfile -Raw
        
        # Проверка multi-stage build
        if ($content -match "FROM.*AS") {
            Write-Success "  Multi-stage build используется"
        } else {
            Write-Warning-Custom "  Multi-stage build не используется в $dockerfile"
        }
        
        # Проверка health check
        if ($content -match "HEALTHCHECK") {
            Write-Success "  Health check настроен"
        } else {
            Write-Warning-Custom "  Health check не настроен в $dockerfile"
        }
    } else {
        Write-Error-Custom "Не найден $dockerfile"
    }
}

# 6. Итоговый отчет
Write-Host "`n📋 ИТОГОВЫЙ ОТЧЕТ" -ForegroundColor Blue
Write-Host "=================="

Write-Host "Найдено ошибок: $Errors" -ForegroundColor $(if ($Errors -eq 0) { "Green" } else { "Red" })
Write-Host "Найдено предупреждений: $Warnings" -ForegroundColor $(if ($Warnings -eq 0) { "Green" } else { "Yellow" })

if ($Errors -eq 0 -and $Warnings -eq 0) {
    Write-Host "`n🎉 ОТЛИЧНО! Проект полностью готов к продакшену" -ForegroundColor Green
    exit 0
} elseif ($Errors -eq 0) {
    Write-Host "`n⚠️  Проект готов к продакшену с незначительными замечаниями" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "`n❌ Проект НЕ готов к продакшену. Необходимо исправить ошибки" -ForegroundColor Red
    exit 1
}
