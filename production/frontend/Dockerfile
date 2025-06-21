# production/frontend/Dockerfile
# Multi-stage build для оптимизации

# Стадия 1: Сборка приложения
FROM node:20-alpine as builder

# Метаданные
LABEL stage=builder

# Установка системных зависимостей
RUN apk add --no-cache git

# Создание рабочей директории
WORKDIR /app

# Копирование package files
COPY frontend/package*.json ./

# Установка зависимостей
RUN npm ci --only=production --silent

# Копирование исходного кода
COPY frontend/ ./
COPY production/frontend/vite.config.js ./vite.config.js

# Установка переменных окружения для сборки
ENV NODE_ENV=production
ENV VITE_API_URL=https://chartgenius-api-europe-west1-a.run.app

# Сборка приложения
RUN npm run build

# Стадия 2: Продакшн сервер
FROM nginx:1.25-alpine

# Метаданные образа
LABEL maintainer="ChartGenius Team"
LABEL version="1.0.0"
LABEL description="ChartGenius Frontend Production"

# Установка дополнительных пакетов
RUN apk add --no-cache curl

# Удаление дефолтной конфигурации nginx
RUN rm /etc/nginx/conf.d/default.conf

# Копирование собранного приложения
COPY --from=builder /app/dist /usr/share/nginx/html

# Копирование продакшн конфигурации nginx
COPY production/frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Создание пользователя для nginx
RUN addgroup -g 1001 -S nginx-user && \
    adduser -S -D -H -u 1001 -h /var/cache/nginx -s /sbin/nologin -G nginx-user -g nginx-user nginx-user

# Настройка прав доступа
RUN chown -R nginx-user:nginx-user /usr/share/nginx/html && \
    chown -R nginx-user:nginx-user /var/cache/nginx && \
    chown -R nginx-user:nginx-user /var/log/nginx && \
    chown -R nginx-user:nginx-user /etc/nginx/conf.d

# Создание директории для PID файла
RUN touch /var/run/nginx.pid && \
    chown -R nginx-user:nginx-user /var/run/nginx.pid

# Переключение на непривилегированного пользователя
USER nginx-user

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

# Экспорт порта
EXPOSE 80

# Команда запуска
CMD ["nginx", "-g", "daemon off;"]
