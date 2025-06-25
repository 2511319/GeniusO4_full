# 🚀 ChartGenius Development Makefile
# Версия: 1.1.0-dev

.PHONY: help install start stop restart logs test build clean status

# Цвета для вывода
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m # No Color

help: ## Показать справку
	@echo "🚀 ChartGenius Development Environment"
	@echo "Версия: 1.1.0-dev"
	@echo ""
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Установить зависимости
	@echo "📦 Установка зависимостей..."
	cd frontend-dev && npm install
	@echo "✅ Зависимости установлены!"

start: ## Запустить dev-окружение
	@echo "🚀 Запуск development окружения..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "✅ Сервисы запущены!"
	@echo "🌐 Frontend: http://localhost:3001"
	@echo "🔧 Backend: http://localhost:8001"
	@echo "🤖 Bot: http://localhost:8002"

stop: ## Остановить dev-окружение
	@echo "🛑 Остановка development окружения..."
	docker-compose -f docker-compose.dev.yml down
	@echo "✅ Сервисы остановлены!"

restart: stop start ## Перезапустить dev-окружение

logs: ## Показать логи всех сервисов
	docker-compose -f docker-compose.dev.yml logs -f

logs-frontend: ## Показать логи фронтенда
	docker-compose -f docker-compose.dev.yml logs -f frontend-dev

logs-backend: ## Показать логи бэкенда
	docker-compose -f docker-compose.dev.yml logs -f backend-dev

logs-bot: ## Показать логи бота
	docker-compose -f docker-compose.dev.yml logs -f bot-dev

test: ## Запустить тесты
	@echo "🧪 Запуск тестов..."
	cd frontend-dev && npm run test

build: ## Собрать проект для разработки
	@echo "🔨 Сборка проекта..."
	cd frontend-dev && npm run build:dev
	@echo "✅ Сборка завершена!"

clean: ## Очистить временные файлы
	@echo "🧹 Очистка временных файлов..."
	docker-compose -f docker-compose.dev.yml down -v
	docker system prune -f
	cd frontend-dev && rm -rf node_modules/.cache
	@echo "✅ Очистка завершена!"

status: ## Показать статус сервисов
	@echo "📊 Статус development сервисов:"
	docker-compose -f docker-compose.dev.yml ps

dev-frontend: ## Запустить только фронтенд локально
	@echo "🎨 Запуск фронтенда в dev режиме..."
	cd frontend-dev && npm run dev

dev-backend: ## Запустить только бэкенд локально
	@echo "⚙️ Запуск бэкенда в dev режиме..."
	cd backend-dev && python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload

check-ports: ## Проверить занятые порты
	@echo "🔍 Проверка портов development:"
	@netstat -an | findstr "3001 8001 8002" || echo "Порты свободны"

switch-to-dev: ## Переключиться на ветку development
	@echo "🔄 Переключение на ветку development..."
	git checkout development
	git pull origin development
	@echo "✅ Переключение завершено!"

version: ## Показать версию
	@echo "📋 Версия development: $(shell cat VERSION)"
	@echo "🌿 Текущая ветка: $(shell git branch --show-current)"
	@echo "📁 Рабочая директория: $(shell pwd)"
