// production/frontend/src/config.js
// Конфигурация для продакшн версии Frontend

// API URL - используем переменную окружения или fallback
export const API_URL = window.ENV?.VITE_API_URL || 'https://chartgenius-api-169129692197.europe-west1.run.app';

// Версия приложения
export const APP_VERSION = '1.0.2';

// Режим отладки
export const DEBUG = false;

// Конфигурация для API запросов
export const API_CONFIG = {
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
};

// Информация о сборке
export const BUILD_INFO = {
  buildTime: new Date().toISOString(),
  environment: 'production',
  apiMode: 'direct'
};

// Console.log отключен в продакшн
if (DEBUG) {
  console.log('Production Config:', {
    API_URL,
    APP_VERSION,
    DEBUG,
    BUILD_INFO
  });
}
