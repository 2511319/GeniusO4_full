# production/backend/Dockerfile
# Multi-stage build для оптимизации размера образа

# Стадия 1: Сборка зависимостей
FROM python:3.10-slim as builder

# Установка системных зависимостей для сборки
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Создание виртуального окружения
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копирование и установка зависимостей
COPY production/backend/requirements.txt /tmp/requirements.txt
COPY production/backend/requirements-production.txt /tmp/requirements-production.txt

# Установка зависимостей
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install --no-cache-dir -r /tmp/requirements-production.txt

# Стадия 2: Продакшн образ
FROM python:3.10-slim

# Метаданные образа
LABEL maintainer="ChartGenius Team"
LABEL version="1.0.0"
LABEL description="ChartGenius API Production"

# Создание пользователя для безопасности
RUN groupadd -r chartgenius && useradd -r -g chartgenius chartgenius

# Установка только runtime зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование виртуального окружения из builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Создание рабочей директории
WORKDIR /app

# Копирование кода приложения
COPY backend/ /app/backend/
COPY production/backend/ /app/production/backend/
COPY configs/ /app/configs/

# Создание директорий для логов
RUN mkdir -p /app/logs

# Переключение на непривилегированного пользователя
USER chartgenius

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production
ENV SERVER_PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://127.0.0.1:${SERVER_PORT:-8080}/health || exit 1

# Экспорт порта
EXPOSE 8080

# Команда запуска
CMD ["python", "production/backend/app.py"]
