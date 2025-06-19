import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Chip,
  Alert,
  CircularProgress,
  Grid,
  Divider
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Warning as WarningIcon
} from '@mui/icons-material';

export default function SubscriptionManager({ telegramId }) {
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSubscription();
  }, [telegramId]);

  const fetchSubscription = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/user/subscription', {
        headers: {
          'X-Telegram-Id': telegramId
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSubscription(data);
      } else {
        setError('Не удалось загрузить информацию о подписке');
      }
    } catch (err) {
      setError('Ошибка при загрузке данных');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (level) => {
    switch (level) {
      case 'premium':
        return 'success';
      case 'basic':
        return 'warning';
      case 'expired':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (level) => {
    switch (level) {
      case 'premium':
      case 'basic':
        return <CheckCircleIcon />;
      case 'expired':
        return <WarningIcon />;
      default:
        return <CancelIcon />;
    }
  };

  const getStatusText = (level) => {
    switch (level) {
      case 'premium':
        return 'Премиум подписка';
      case 'basic':
        return 'Базовая подписка';
      case 'expired':
        return 'Подписка истекла';
      default:
        return 'Подписка отсутствует';
    }
  };

  const handleSubscribe = async (level = 'premium') => {
    try {
      const response = await fetch('/api/user/subscription/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Telegram-Id': telegramId
        },
        body: JSON.stringify({
          level: level,
          duration_days: level === 'premium' ? 30 : 7
        })
      });

      if (response.ok) {
        await fetchSubscription();
      } else {
        setError('Не удалось оформить подписку');
      }
    } catch (err) {
      setError('Ошибка при оформлении подписки');
    }
  };

  const handleRenew = async () => {
    try {
      const response = await fetch('/api/user/subscription/renew', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Telegram-Id': telegramId
        },
        body: JSON.stringify({
          level: subscription?.level || 'premium',
          duration_days: 30
        })
      });

      if (response.ok) {
        await fetchSubscription();
      } else {
        setError('Не удалось продлить подписку');
      }
    } catch (err) {
      setError('Ошибка при продлении подписки');
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          💳 Управление подпиской
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {subscription && (
          <Box>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              <Chip
                icon={getStatusIcon(subscription.level)}
                label={getStatusText(subscription.level)}
                color={getStatusColor(subscription.level)}
                variant="outlined"
              />
            </Box>

            {subscription.expires_at && (
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Действует до: {new Date(subscription.expires_at).toLocaleDateString('ru-RU')}
              </Typography>
            )}

            <Divider sx={{ my: 2 }} />

            <Grid container spacing={2}>
              {!subscription.is_active ? (
                <>
                  <Grid item xs={12} sm={6}>
                    <Button
                      variant="contained"
                      color="warning"
                      fullWidth
                      onClick={() => handleSubscribe('basic')}
                    >
                      Базовая подписка
                      <br />
                      <Typography variant="caption">7 дней</Typography>
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Button
                      variant="contained"
                      color="primary"
                      fullWidth
                      onClick={() => handleSubscribe('premium')}
                    >
                      Премиум подписка
                      <br />
                      <Typography variant="caption">30 дней</Typography>
                    </Button>
                  </Grid>
                </>
              ) : (
                <Grid item xs={12}>
                  <Button
                    variant="contained"
                    color="success"
                    fullWidth
                    onClick={handleRenew}
                  >
                    Продлить подписку
                  </Button>
                </Grid>
              )}
            </Grid>

            <Box mt={2}>
              <Typography variant="h6" gutterBottom>
                Возможности подписки:
              </Typography>
              <Typography variant="body2" component="div">
                <strong>Базовая:</strong>
                <ul>
                  <li>Базовый технический анализ</li>
                  <li>Основные индикаторы</li>
                  <li>Простые рекомендации</li>
                </ul>
                <strong>Премиум:</strong>
                <ul>
                  <li>Полный технический анализ</li>
                  <li>Все индикаторы и паттерны</li>
                  <li>Прогнозирование цен</li>
                  <li>Детальные торговые рекомендации</li>
                  <li>Интерактивные графики</li>
                </ul>
              </Typography>
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
