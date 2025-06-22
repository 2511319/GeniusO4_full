// frontend/src/config.js
// Конфигурация для development версии Frontend

// API URL - для development используем относительные пути через proxy
export const API_URL = '';

// Версия приложения (синхронизировано с production/VERSION)
export const APP_VERSION = '1.0.2';

// Режим отладки
export const DEBUG = true;

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
  environment: 'development',
  apiMode: 'proxy'
};

if (DEBUG) {
  console.log('Development Config:', {
    API_URL: API_URL || 'relative paths (proxy)',
    APP_VERSION,
    DEBUG,
    BUILD_INFO
  });
}
