#!/bin/bash
# 🚀 ChartGenius Development Environment Startup Script
# Версия: 1.1.0-dev
# Автоматический запуск всех сервисов для разработки

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Функция для вывода заголовков
print_header() {
    echo -e "\n${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}\n"
}

# Функция для вывода успеха
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Функция для вывода предупреждения
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Функция для вывода ошибки
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Функция для вывода информации
print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Проверка зависимостей
check_dependencies() {
    print_header "Проверка зависимостей"
    
    # Проверка Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker не установлен. Установите Docker и попробуйте снова."
        exit 1
    fi
    print_success "Docker установлен"
    
    # Проверка Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
        exit 1
    fi
    print_success "Docker Compose установлен"
    
    # Проверка .env файла
    if [ ! -f ".env.development" ]; then
        print_warning ".env.development не найден. Создаю из примера..."
        if [ -f ".env.development.example" ]; then
            cp .env.development.example .env.development
            print_info "Отредактируйте .env.development с вашими API ключами"
        else
            print_error ".env.development.example не найден"
            exit 1
        fi
    fi
    print_success ".env.development найден"
    
    # Проверка service account
    if [ ! -f "service-account.json" ]; then
        print_warning "service-account.json не найден"
        print_info "Поместите ваш Google Cloud service account файл как service-account.json"
        print_info "Или создайте пустой файл для тестирования: echo '{}' > service-account.json"
    else
        print_success "service-account.json найден"
    fi
}

# Остановка существующих контейнеров
stop_existing() {
    print_header "Остановка существующих контейнеров"
    
    docker-compose -f docker-compose.dev.yml down --remove-orphans 2>/dev/null || true
    docker-compose -f monitoring/docker-compose.monitoring.yml down --remove-orphans 2>/dev/null || true
    
    print_success "Существующие контейнеры остановлены"
}

# Сборка образов
build_images() {
    print_header "Сборка Docker образов"
    
    print_info "Сборка backend образа..."
    docker-compose -f docker-compose.dev.yml build backend-dev
    
    print_info "Сборка frontend образа..."
    docker-compose -f docker-compose.dev.yml build frontend-dev
    
    print_info "Сборка bot образа..."
    docker-compose -f docker-compose.dev.yml build bot-dev
    
    print_success "Все образы собраны"
}

# Запуск основных сервисов
start_main_services() {
    print_header "Запуск основных сервисов"
    
    print_info "Запуск Redis..."
    docker-compose -f docker-compose.dev.yml up -d redis-dev
    sleep 5
    
    print_info "Запуск Celery Worker..."
    docker-compose -f docker-compose.dev.yml up -d celery-worker-dev
    sleep 5
    
    print_info "Запуск Backend API..."
    docker-compose -f docker-compose.dev.yml up -d backend-dev
    sleep 10
    
    print_info "Запуск Frontend..."
    docker-compose -f docker-compose.dev.yml up -d frontend-dev
    sleep 5
    
    print_info "Запуск Telegram Bot..."
    docker-compose -f docker-compose.dev.yml up -d bot-dev
    sleep 5
    
    print_success "Основные сервисы запущены"
}

# Запуск мониторинга
start_monitoring() {
    print_header "Запуск мониторинга (опционально)"
    
    read -p "Запустить мониторинг (Prometheus + Grafana)? [y/N]: " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Запуск мониторинга..."
        docker-compose -f monitoring/docker-compose.monitoring.yml up -d
        sleep 10
        print_success "Мониторинг запущен"
    else
        print_info "Мониторинг пропущен"
    fi
}

# Проверка здоровья сервисов
check_health() {
    print_header "Проверка здоровья сервисов"
    
    # Ожидание запуска сервисов
    print_info "Ожидание запуска сервисов (30 секунд)..."
    sleep 30
    
    # Проверка Backend
    print_info "Проверка Backend API..."
    if curl -s http://localhost:8001/health > /dev/null; then
        print_success "Backend API работает"
    else
        print_warning "Backend API недоступен"
    fi
    
    # Проверка Frontend
    print_info "Проверка Frontend..."
    if curl -s http://localhost:3001 > /dev/null; then
        print_success "Frontend работает"
    else
        print_warning "Frontend недоступен"
    fi
    
    # Проверка Redis
    print_info "Проверка Redis..."
    if docker exec chartgenius-redis-dev redis-cli ping > /dev/null 2>&1; then
        print_success "Redis работает"
    else
        print_warning "Redis недоступен"
    fi
    
    # Проверка Celery
    print_info "Проверка Celery Worker..."
    if docker-compose -f docker-compose.dev.yml ps celery-worker-dev | grep -q "Up"; then
        print_success "Celery Worker работает"
    else
        print_warning "Celery Worker недоступен"
    fi
}

# Вывод информации о доступе
show_access_info() {
    print_header "Информация о доступе к сервисам"
    
    echo -e "${CYAN}🌐 Web сервисы:${NC}"
    echo -e "   Frontend:      ${GREEN}http://localhost:3001${NC}"
    echo -e "   Backend API:   ${GREEN}http://localhost:8001${NC}"
    echo -e "   Swagger UI:    ${GREEN}http://localhost:8001/docs${NC}"
    echo -e "   ReDoc:         ${GREEN}http://localhost:8001/redoc${NC}"
    echo -e "   Admin Panel:   ${GREEN}http://localhost:3001/admin${NC}"
    
    echo -e "\n${PURPLE}🔧 Инфраструктура:${NC}"
    echo -e "   Redis:         ${GREEN}localhost:6380${NC}"
    echo -e "   Bot Webhook:   ${GREEN}http://localhost:8002${NC}"
    
    if docker-compose -f monitoring/docker-compose.monitoring.yml ps | grep -q "Up"; then
        echo -e "\n${YELLOW}📊 Мониторинг:${NC}"
        echo -e "   Prometheus:    ${GREEN}http://localhost:9090${NC}"
        echo -e "   Grafana:       ${GREEN}http://localhost:3000${NC} (admin/admin)"
        echo -e "   Redis UI:      ${GREEN}http://localhost:8081${NC}"
    fi
    
    echo -e "\n${BLUE}🔌 WebSocket:${NC}"
    echo -e "   WebSocket:     ${GREEN}ws://localhost:8001/ws/{user_id}${NC}"
    
    echo -e "\n${GREEN}📋 Полезные команды:${NC}"
    echo -e "   Логи всех сервисов:    ${CYAN}docker-compose -f docker-compose.dev.yml logs -f${NC}"
    echo -e "   Логи backend:          ${CYAN}docker-compose -f docker-compose.dev.yml logs -f backend-dev${NC}"
    echo -e "   Остановка:             ${CYAN}docker-compose -f docker-compose.dev.yml down${NC}"
    echo -e "   Перезапуск:            ${CYAN}./start-dev.sh${NC}"
    
    echo -e "\n${YELLOW}📚 Документация:${NC}"
    echo -e "   README:        ${CYAN}development/README.md${NC}"
    echo -e "   API Docs:      ${CYAN}development/docs/API.md${NC}"
    echo -e "   Architecture:  ${CYAN}development/docs/ARCHITECTURE.md${NC}"
}

# Основная функция
main() {
    clear
    echo -e "${PURPLE}"
    echo "  ██████╗██╗  ██╗ █████╗ ██████╗ ████████╗ ██████╗ ███████╗███╗   ██╗██╗██╗   ██╗███████╗"
    echo " ██╔════╝██║  ██║██╔══██╗██╔══██╗╚══██╔══╝██╔════╝ ██╔════╝████╗  ██║██║██║   ██║██╔════╝"
    echo " ██║     ███████║███████║██████╔╝   ██║   ██║  ███╗█████╗  ██╔██╗ ██║██║██║   ██║███████╗"
    echo " ██║     ██╔══██║██╔══██║██╔══██╗   ██║   ██║   ██║██╔══╝  ██║╚██╗██║██║██║   ██║╚════██║"
    echo " ╚██████╗██║  ██║██║  ██║██║  ██║   ██║   ╚██████╔╝███████╗██║ ╚████║██║╚██████╔╝███████║"
    echo "  ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚══════╝"
    echo -e "${NC}"
    echo -e "${CYAN}                          Development Environment v1.1.0-dev${NC}"
    echo -e "${CYAN}                               Startup Script${NC}\n"
    
    # Выполнение шагов
    check_dependencies
    stop_existing
    build_images
    start_main_services
    start_monitoring
    check_health
    show_access_info
    
    print_header "🎉 ChartGenius Development Environment готов!"
    print_success "Все сервисы запущены и готовы к работе"
    print_info "Нажмите Ctrl+C для остановки или используйте: docker-compose -f docker-compose.dev.yml down"
    
    # Опция следить за логами
    echo
    read -p "Показать логи в реальном времени? [y/N]: " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Показ логов (Ctrl+C для выхода)..."
        docker-compose -f docker-compose.dev.yml logs -f
    fi
}

# Обработка сигналов
trap 'echo -e "\n${YELLOW}Получен сигнал остановки...${NC}"; exit 0' INT TERM

# Запуск основной функции
main "$@"
