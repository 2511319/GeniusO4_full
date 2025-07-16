# ChartGenius v3 Backend Dockerfile
# Optimized for Oracle Cloud Always Free Tier

# Stage 1: Build stage
FROM python:3.11-slim as builder

# Устанавливаем системные зависимости для сборки
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libc6-dev \
    libffi-dev \
    libssl-dev \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Создаем виртуальное окружение
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.11-slim

# Устанавливаем только runtime зависимости
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Копируем виртуальное окружение из builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Создаем пользователя для безопасности
RUN groupadd -r chartgenius && useradd -r -g chartgenius chartgenius

# Создаем рабочую директорию
WORKDIR /app

# Копируем код приложения
COPY --chown=chartgenius:chartgenius . .

# Создаем директории для логов и данных
RUN mkdir -p logs data && chown -R chartgenius:chartgenius logs data

# Переключаемся на непривилегированного пользователя
USER chartgenius

# Открываем порт
EXPOSE 8000

# Health check оптимизированный для Oracle Cloud
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Команда запуска оптимизированная для Always Free (1 worker)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--access-log"]
