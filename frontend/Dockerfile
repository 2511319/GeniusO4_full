# frontend/Dockerfile
FROM node:20 AS build
WORKDIR /app

# Копируем package files
COPY frontend/package*.json ./
RUN npm install

# Копируем исходный код
COPY frontend/ .

# Аргументы сборки для переменных окружения
ARG VITE_API_URL
ARG VITE_TELEGRAM_BOT_USERNAME

# Устанавливаем переменные окружения для Vite
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_TELEGRAM_BOT_USERNAME=$VITE_TELEGRAM_BOT_USERNAME

# Собираем приложение
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Копируем конфигурацию nginx для SPA
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
