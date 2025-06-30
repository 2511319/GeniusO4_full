# scripts/check-config-simple.ps1
# Simple production readiness check for ChartGenius

Write-Host "ChartGenius Production Readiness Check" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

$Errors = 0
$Warnings = 0

function Write-Error-Custom($message) {
    Write-Host "ERROR: $message" -ForegroundColor Red
    $script:Errors++
}

function Write-Warning-Custom($message) {
    Write-Host "WARNING: $message" -ForegroundColor Yellow
    $script:Warnings++
}

function Write-Success($message) {
    Write-Host "OK: $message" -ForegroundColor Green
}

# 1. Check versions
Write-Host "`nChecking versions..." -ForegroundColor Blue

$ProdVersion = if (Test-Path "production/VERSION") { 
    (Get-Content "production/VERSION" -Raw).Trim() 
} else { "NOT_FOUND" }

$FrontendVersion = if (Test-Path "frontend/package.json") { 
    (Get-Content "frontend/package.json" | ConvertFrom-Json).version 
} else { "NOT_FOUND" }

Write-Host "Production VERSION: $ProdVersion"
Write-Host "Frontend package.json: $FrontendVersion"

if ($ProdVersion -eq $FrontendVersion -and $ProdVersion -ne "NOT_FOUND") {
    Write-Success "Versions are synchronized"
} else {
    Write-Error-Custom "Versions are not synchronized"
}

# 2. Check for localhost in production files
Write-Host "`nChecking for localhost in production files..." -ForegroundColor Blue

$LocalhostFound = $false
if (Test-Path "production") {
    Get-ChildItem -Path "production" -Recurse -File | ForEach-Object {
        try {
            $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
            if ($content -and ($content -match "localhost" -or ($content -match "127\.0\.0\.1" -and $content -notmatch "HEALTHCHECK"))) {
                Write-Host "Found localhost in: $($_.Name)" -ForegroundColor Red
                $LocalhostFound = $true
            }
        } catch {
            # Skip files that can't be read
        }
    }
}

if ($LocalhostFound) {
    Write-Error-Custom "Found localhost in production files"
} else {
    Write-Success "No localhost found in production files"
}

# 3. Check API URLs consistency
Write-Host "`nChecking API URLs consistency..." -ForegroundColor Blue

$ApiUrls = @()

if (Test-Path "production/frontend/nginx.conf") {
    $content = Get-Content "production/frontend/nginx.conf" -Raw
    if ($content -match "https://[^;\s]+\.run\.app") {
        $ApiUrls += $matches[0]
        Write-Host "Nginx API URL: $($matches[0])"
    }
}

if (Test-Path "production/frontend/Dockerfile") {
    $content = Get-Content "production/frontend/Dockerfile" -Raw
    if ($content -match "https://[^\s]+\.run\.app") {
        $ApiUrls += $matches[0]
        Write-Host "Dockerfile API URL: $($matches[0])"
    }
}

if (Test-Path "production/frontend/src/config.js") {
    $content = Get-Content "production/frontend/src/config.js" -Raw
    if ($content -match "https://[^'`"]+\.run\.app") {
        $ApiUrls += $matches[0]
        Write-Host "Config API URL: $($matches[0])"
    }
}

$UniqueUrls = $ApiUrls | Select-Object -Unique
if ($UniqueUrls.Count -eq 1) {
    Write-Success "API URLs are consistent"
} elseif ($UniqueUrls.Count -gt 1) {
    Write-Error-Custom "API URLs are inconsistent"
    $UniqueUrls | ForEach-Object { Write-Host "  - $_" }
} else {
    Write-Warning-Custom "No API URLs found in production files"
}

# 4. Check for real secrets
Write-Host "`nChecking for real secrets..." -ForegroundColor Blue

$SecretsFound = $false
Get-ChildItem -Recurse -File -Include "*.ps1", "*.py", "*.js" | Where-Object {
    $_.DirectoryName -notmatch "node_modules" -and $_.Name -notmatch "check-.*\.ps1"
} | ForEach-Object {
    try {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -and $content -match "REAL_TELEGRAM_TOKEN_PATTERN_REMOVED:" -and $_.Name -notmatch "\.md$") {
            Write-Host "Found real Telegram token in: $($_.Name)" -ForegroundColor Red
            $SecretsFound = $true
        }
    } catch {
        # Skip files that can't be read
    }
}

if ($SecretsFound) {
    Write-Error-Custom "Found real secrets in code"
} else {
    Write-Success "No real secrets found in code"
}

# 5. Check Docker files
Write-Host "`nChecking Docker files..." -ForegroundColor Blue

$DockerFiles = @("production/backend/Dockerfile", "production/frontend/Dockerfile", "production/bot/Dockerfile")

foreach ($dockerfile in $DockerFiles) {
    if (Test-Path $dockerfile) {
        Write-Success "Found $dockerfile"
    } else {
        Write-Error-Custom "Missing $dockerfile"
    }
}

# 6. Check required directories
Write-Host "`nChecking project structure..." -ForegroundColor Blue

$RequiredDirs = @("production", "backend", "frontend", "bot")
foreach ($dir in $RequiredDirs) {
    if (Test-Path $dir) {
        Write-Success "Directory $dir exists"
    } else {
        Write-Error-Custom "Directory $dir missing"
    }
}

# Final report
Write-Host "`nFinal Report" -ForegroundColor Blue
Write-Host "============"

Write-Host "Errors found: $Errors" -ForegroundColor $(if ($Errors -eq 0) { "Green" } else { "Red" })
Write-Host "Warnings found: $Warnings" -ForegroundColor $(if ($Warnings -eq 0) { "Green" } else { "Yellow" })

if ($Errors -eq 0 -and $Warnings -eq 0) {
    Write-Host "`nProject is READY for production!" -ForegroundColor Green
    exit 0
} elseif ($Errors -eq 0) {
    Write-Host "`nProject is ready for production with minor warnings" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "`nProject is NOT ready for production. Fix errors first." -ForegroundColor Red
    exit 1
}
