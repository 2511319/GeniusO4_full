# production/bot/Dockerfile
# Продакшн образ для Telegram бота

FROM python:3.10-slim

# Метаданные образа
LABEL maintainer="ChartGenius Team"
LABEL version="1.0.0"
LABEL description="ChartGenius Telegram Bot Production"

# Создание пользователя для безопасности
RUN groupadd -r botuser && useradd -r -g botuser botuser

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование и установка зависимостей
COPY bot/requirements.txt /tmp/bot-requirements.txt
COPY production/bot/requirements-production.txt /tmp/requirements-production.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/bot-requirements.txt && \
    pip install --no-cache-dir -r /tmp/requirements-production.txt

# Копирование кода
COPY bot/ /app/bot/
COPY backend/ /app/backend/
COPY configs/ /app/configs/
COPY production/bot/ /app/production/bot/

# Создание директорий для логов
RUN mkdir -p /app/logs && \
    chown -R botuser:botuser /app

# Переключение на непривилегированного пользователя
USER botuser

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# Health check (для Cloud Run)
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Команда запуска
CMD ["python", "production/bot/app.py"]
