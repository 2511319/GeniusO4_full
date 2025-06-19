import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Avatar,
  Chip,
  Button,
  Tabs,
  Tab,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  Person as PersonIcon,
  Analytics as AnalyticsIcon,
  History as HistoryIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import SubscriptionManager from '../components/SubscriptionManager';
import AnalysisSelector from '../components/AnalysisSelector';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`dashboard-tabpanel-${index}`}
      aria-labelledby={`dashboard-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export default function UserDashboard() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);
  const [userProfile, setUserProfile] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Получаем telegram_id из токена или параметров
  const token = searchParams.get('token');
  const telegramId = searchParams.get('telegram_id') || extractTelegramIdFromToken(token);

  function extractTelegramIdFromToken(token) {
    if (!token) return null;
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.telegram_id || payload.sub;
    } catch {
      return null;
    }
  }

  useEffect(() => {
    if (!telegramId) {
      setError('Не удалось определить пользователя');
      return;
    }
    fetchUserData();
  }, [telegramId]);

  const fetchUserData = async () => {
    try {
      setLoading(true);
      
      // Загружаем профиль пользователя
      const profileResponse = await fetch('/api/user/profile', {
        headers: { 'X-Telegram-Id': telegramId }
      });
      
      if (profileResponse.ok) {
        const profileData = await profileResponse.json();
        setUserProfile(profileData);
        setSubscription(profileData.subscription);
      }

      // Загружаем список анализов
      const analysesResponse = await fetch('/api/user/analyses', {
        headers: { 'X-Telegram-Id': telegramId }
      });
      
      if (analysesResponse.ok) {
        const analysesData = await analysesResponse.json();
        setAnalyses(analysesData.analyses || []);
      }

    } catch (err) {
      setError('Ошибка при загрузке данных пользователя');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalysisSelect = (analysisType) => {
    // Перенаправляем на страницу анализа с выбранным типом
    const params = new URLSearchParams({
      token: token,
      analysis_type: analysisType.id
    });
    navigate(`/?${params.toString()}`);
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Заголовок профиля */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={2}>
            <Avatar sx={{ width: 64, height: 64, bgcolor: 'primary.main' }}>
              {userProfile?.photo_url ? (
                <img src={userProfile.photo_url} alt="Profile" style={{ width: '100%', height: '100%' }} />
              ) : (
                <PersonIcon fontSize="large" />
              )}
            </Avatar>
            <Box flex={1}>
              <Typography variant="h4" gutterBottom>
                Добро пожаловать, {userProfile?.first_name || 'Пользователь'}!
              </Typography>
              <Box display="flex" gap={1} alignItems="center">
                <Typography variant="body2" color="text.secondary">
                  ID: {userProfile?.id}
                </Typography>
                {userProfile?.username && (
                  <Typography variant="body2" color="text.secondary">
                    • @{userProfile.username}
                  </Typography>
                )}
                <Chip
                  label={subscription?.is_active ? 
                    (subscription.level === 'premium' ? 'Премиум' : 'Базовая') : 
                    'Нет подписки'
                  }
                  color={subscription?.is_active ? 'success' : 'default'}
                  size="small"
                />
              </Box>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Навигационные вкладки */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="dashboard tabs">
            <Tab icon={<AnalyticsIcon />} label="Анализ" />
            <Tab icon={<PersonIcon />} label="Подписка" />
            <Tab icon={<HistoryIcon />} label="История" />
            <Tab icon={<SettingsIcon />} label="Настройки" />
          </Tabs>
        </Box>

        {/* Вкладка анализа */}
        <TabPanel value={tabValue} index={0}>
          <AnalysisSelector 
            onAnalysisSelect={handleAnalysisSelect}
            subscription={subscription}
          />
        </TabPanel>

        {/* Вкладка подписки */}
        <TabPanel value={tabValue} index={1}>
          <SubscriptionManager 
            telegramId={telegramId}
          />
        </TabPanel>

        {/* Вкладка истории */}
        <TabPanel value={tabValue} index={2}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                📈 История анализов
              </Typography>
              {analyses.length > 0 ? (
                <Grid container spacing={2}>
                  {analyses.map((analysis) => (
                    <Grid item xs={12} sm={6} md={4} key={analysis.id}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6">{analysis.symbol}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            {new Date(analysis.created_at).toLocaleDateString('ru-RU')}
                          </Typography>
                          <Chip 
                            label={analysis.type === 'full' ? 'Полный' : 'Краткий'}
                            size="small"
                            color={analysis.type === 'full' ? 'primary' : 'secondary'}
                            sx={{ mt: 1 }}
                          />
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  У вас пока нет выполненных анализов
                </Typography>
              )}
            </CardContent>
          </Card>
        </TabPanel>

        {/* Вкладка настроек */}
        <TabPanel value={tabValue} index={3}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                ⚙️ Настройки
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Настройки будут добавлены в следующих версиях
              </Typography>
            </CardContent>
          </Card>
        </TabPanel>
      </Card>
    </Container>
  );
}
