import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  
  // Продакшн настройки
  build: {
    outDir: 'dist',
    sourcemap: false, // Отключаем source maps в продакшн
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          mui: ['@mui/material', '@mui/icons-material'],
          charts: ['lightweight-charts'],
          redux: ['@reduxjs/toolkit', 'react-redux']
        }
      }
    },
    // Оптимизация размера бандла
    chunkSizeWarningLimit: 1000,
    target: 'es2020'
  },
  
  // Настройки сервера для разработки
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'https://chartgenius-backend-169129692197.europe-west1.run.app',
        changeOrigin: true,
        secure: true
      }
    }
  },
  
  // Переменные окружения
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  },
  
  // Оптимизация
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      '@mui/material',
      '@mui/icons-material',
      'lightweight-charts',
      '@reduxjs/toolkit',
      'react-redux'
    ]
  }
});
