import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  Chip,
  Alert,
  CircularProgress,
  Divider
} from '@mui/material';
import {
  Person as PersonIcon,
  Star as StarIcon,
  Schedule as ScheduleIcon,
  Analytics as AnalyticsIcon
} from '@mui/icons-material';
import { clearAuth } from '../store';

export default function UserDashboard() {
  const { token } = useSelector((state) => state.auth);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  
  const [userInfo, setUserInfo] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) {
      navigate('/');
      return;
    }
    
    loadUserData();
  }, [token, navigate]);

  const loadUserData = async () => {
    try {
      setLoading(true);
      
      // Извлекаем данные пользователя из JWT токена
      const payload = JSON.parse(atob(token.split('.')[1]));
      const telegramId = payload.telegram_id;
      
      // Здесь можно добавить запрос к API для получения дополнительной информации
      // Пока используем данные из токена
      setUserInfo({
        telegram_id: telegramId,
        role: 'user', // По умолчанию
        created_at: new Date().toISOString()
      });
      
      // Заглушка для подписки
      setSubscription({
        level: 'free',
        expires_at: null
      });
      
    } catch (err) {
      console.error('Ошибка загрузки данных пользователя:', err);
      setError('Не удалось загрузить данные пользователя');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    dispatch(clearAuth());
    navigate('/');
  };

  const handleBackToAnalysis = () => {
    navigate('/');
  };

  const getRoleColor = (role) => {
    const colors = {
      'admin': 'error',
      'moderator': 'warning', 
      'vip': 'secondary',
      'premium': 'primary',
      'user': 'default'
    };
    return colors[role] || 'default';
  };

  const getRoleLabel = (role) => {
    const labels = {
      'admin': '👑 Администратор',
      'moderator': '🛡️ Модератор',
      'vip': '💎 VIP',
      'premium': '⭐ Premium',
      'user': '👤 Пользователь'
    };
    return labels[role] || '👤 Пользователь';
  };

  const getSubscriptionColor = (level) => {
    const colors = {
      'vip': 'secondary',
      'premium': 'primary',
      'free': 'default',
      'expired': 'error'
    };
    return colors[level] || 'default';
  };

  const getSubscriptionLabel = (level) => {
    const labels = {
      'vip': '💎 VIP подписка',
      'premium': '⭐ Premium подписка', 
      'free': '🆓 Бесплатный доступ',
      'expired': '⏰ Подписка истекла'
    };
    return labels[level] || '🆓 Бесплатный доступ';
  };

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Загрузка данных...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" color="primary">
            👤 Личный кабинет
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button 
              variant="outlined" 
              onClick={handleBackToAnalysis}
              startIcon={<AnalyticsIcon />}
            >
              К анализу
            </Button>
            <Button 
              variant="outlined" 
              color="error" 
              onClick={handleLogout}
            >
              Выйти
            </Button>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Информация о пользователе */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <PersonIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">Информация о пользователе</Typography>
                </Box>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Telegram ID:
                  </Typography>
                  <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
                    {userInfo?.telegram_id}
                  </Typography>
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Роль:
                  </Typography>
                  <Chip 
                    label={getRoleLabel(userInfo?.role)}
                    color={getRoleColor(userInfo?.role)}
                    size="small"
                    sx={{ mt: 0.5 }}
                  />
                </Box>

                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Дата регистрации:
                  </Typography>
                  <Typography variant="body1">
                    {userInfo?.created_at ? 
                      new Date(userInfo.created_at).toLocaleDateString('ru-RU') : 
                      'Недоступно'
                    }
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Информация о подписке */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <StarIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">Подписка</Typography>
                </Box>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Текущий план:
                  </Typography>
                  <Chip 
                    label={getSubscriptionLabel(subscription?.level)}
                    color={getSubscriptionColor(subscription?.level)}
                    size="small"
                    sx={{ mt: 0.5 }}
                  />
                </Box>

                {subscription?.expires_at && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Действует до:
                    </Typography>
                    <Typography variant="body1">
                      {new Date(subscription.expires_at).toLocaleDateString('ru-RU')}
                    </Typography>
                  </Box>
                )}

                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Доступные функции:
                  </Typography>
                  <Box sx={{ mt: 1 }}>
                    <Chip label="📊 Базовый анализ" size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                    {(subscription?.level === 'premium' || subscription?.level === 'vip') && (
                      <Chip label="📋 Watchlist" size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                    )}
                    {subscription?.level === 'vip' && (
                      <Chip label="🎯 VIP поддержка" size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                    )}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Статистика использования */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <ScheduleIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">Статистика использования</Typography>
                </Box>
                
                <Grid container spacing={2}>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary">0</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Анализов сегодня
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary">0</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Всего анализов
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary">0</Typography>
                      <Typography variant="body2" color="text.secondary">
                        В watchlist
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary">
                        {Math.floor((Date.now() - new Date(userInfo?.created_at || Date.now())) / (1000 * 60 * 60 * 24))}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Дней с нами
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />
        
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            ChartGenius v1.0.2 • Профессиональный анализ криптовалютных рынков
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
}
