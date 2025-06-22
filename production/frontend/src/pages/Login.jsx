import React, { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';
import { 
  Container, 
  Paper, 
  Typography, 
  Box, 
  Button, 
  Alert,
  CircularProgress 
} from '@mui/material';
import { setToken } from '../store';

export default function Login() {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [telegramWebApp, setTelegramWebApp] = useState(null);

  useEffect(() => {
    // Проверяем, запущено ли приложение в Telegram WebApp
    if (window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp;
      setTelegramWebApp(tg);
      
      // Настраиваем WebApp
      tg.ready();
      tg.expand();
      
      // Автоматически пытаемся авторизоваться если есть initData
      if (tg.initData) {
        console.log('🔑 Обнаружены данные Telegram WebApp, выполняем автоматическую авторизацию...');
        handleTelegramAuth(tg.initData);
      }
    }
  }, []);

  const handleTelegramAuth = async (initData) => {
    setLoading(true);
    setError('');

    try {
      console.log('📡 Отправляем запрос на авторизацию...');
      
      const response = await fetch('/api/auth/webapp-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'text/plain',
        },
        body: initData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка авторизации');
      }

      const data = await response.json();
      console.log('✅ Авторизация успешна, получен токен');
      
      // Сохраняем токен
      dispatch(setToken(data.access_token));
      
      // Уведомляем Telegram WebApp об успехе
      if (telegramWebApp) {
        telegramWebApp.showAlert('✅ Авторизация успешна!');
      }

    } catch (err) {
      console.error('❌ Ошибка авторизации:', err);
      setError(err.message || 'Произошла ошибка при авторизации');
      
      // Уведомляем Telegram WebApp об ошибке
      if (telegramWebApp) {
        telegramWebApp.showAlert('❌ Ошибка авторизации: ' + err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleManualAuth = () => {
    if (telegramWebApp && telegramWebApp.initData) {
      handleTelegramAuth(telegramWebApp.initData);
    } else {
      setError('Данные Telegram WebApp недоступны. Убедитесь, что приложение запущено через Telegram.');
    }
  };

  const handleOpenInTelegram = () => {
    // Пытаемся открыть Telegram бота для бесшовной авторизации
    const telegramBotUrl = "https://t.me/Chart_Genius_bot";

    try {
      // Открываем Telegram в новой вкладке/приложении
      const opened = window.open(telegramBotUrl, '_blank');

      if (opened) {
        setError('✅ Telegram открыт! Используйте команду /start в боте @Chart_Genius_bot для получения ссылки на приложение.');
      } else {
        // Если popup заблокирован, показываем инструкцию
        setError('🔗 Перейдите к боту @Chart_Genius_bot в Telegram и используйте команду /start');
      }
    } catch (e) {
      // Fallback если не удалось открыть
      setError('📱 Откройте Telegram и найдите бота @Chart_Genius_bot, затем используйте команду /start');
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom color="primary">
          ChartGenius
        </Typography>
        
        <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
          Профессиональный анализ криптовалютных рынков
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ mb: 3 }}>
          {telegramWebApp ? (
            <Box>
              <Typography variant="body1" sx={{ mb: 2 }}>
                🚀 Приложение запущено в Telegram
              </Typography>
              
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 2 }}>
                  <CircularProgress size={24} />
                  <Typography>Выполняется авторизация...</Typography>
                </Box>
              ) : (
                <Button
                  variant="contained"
                  size="large"
                  onClick={handleManualAuth}
                  disabled={loading}
                  sx={{ minWidth: 200 }}
                >
                  🔑 Войти через Telegram
                </Button>
              )}
            </Box>
          ) : (
            <Box>
              <Typography variant="body1" sx={{ mb: 2, color: 'text.secondary' }}>
                Для использования ChartGenius необходимо войти через Telegram
              </Typography>
              
              <Button
                variant="contained"
                size="large"
                onClick={handleOpenInTelegram}
                sx={{
                  minWidth: 200,
                  background: 'linear-gradient(45deg, #0088cc 30%, #229ED9 90%)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #006699 30%, #1a7db8 90%)',
                  }
                }}
              >
                🚀 Запустить в Telegram
              </Button>
            </Box>
          )}
        </Box>

        <Box sx={{ mt: 4, pt: 3, borderTop: '1px solid', borderColor: 'divider' }}>
          <Typography variant="body2" color="text.secondary">
            📊 Технические индикаторы и паттерны<br />
            🎯 Торговые рекомендации<br />
            🔍 Профессиональный анализ рынков
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
}
