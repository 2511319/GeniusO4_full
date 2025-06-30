// 🛠️ Admin Dashboard for ChartGenius
// Версия: 1.1.0-dev
// Главная страница админ-панели

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  Chip,
  Button,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Settings as SettingsIcon,
  Storage as StorageIcon,
  TrendingUp as TrendingUpIcon,
  People as PeopleIcon,
  Refresh as RefreshIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon
} from '@mui/icons-material';

import SystemHealth from '../components/admin/SystemHealth';
import UserManager from '../components/admin/UserManager';
import PromptManager from '../components/admin/PromptManager';
import MarketDataManager from '../components/admin/MarketDataManager';
import TaskMonitor from '../components/admin/TaskMonitor';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`admin-tabpanel-${index}`}
      aria-labelledby={`admin-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const AdminDashboard = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [systemStats, setSystemStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  const tabs = [
    { label: 'Обзор', icon: <DashboardIcon />, component: 'overview' },
    { label: 'Система', icon: <SettingsIcon />, component: 'system' },
    { label: 'Пользователи', icon: <PeopleIcon />, component: 'users' },
    { label: 'Промпты', icon: <StorageIcon />, component: 'prompts' },
    { label: 'Данные', icon: <TrendingUpIcon />, component: 'market' },
    { label: 'Задачи', icon: <StorageIcon />, component: 'tasks' }
  ];

  const fetchSystemStats = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/market/health');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setSystemStats(data);
      setLastUpdate(new Date());

    } catch (err) {
      console.error('Error fetching system stats:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSystemStats();
    
    // Автообновление каждые 30 секунд
    const interval = setInterval(fetchSystemStats, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  const getSystemStatusColor = () => {
    if (!systemStats) return 'default';
    
    const { market_data, system } = systemStats;
    
    // Проверяем статус источников данных
    const healthySources = Object.values(market_data?.sources || {})
      .filter(source => source.status === 'healthy').length;
    const totalSources = Object.keys(market_data?.sources || {}).length;
    
    if (healthySources === totalSources) return 'success';
    if (healthySources > totalSources / 2) return 'warning';
    return 'error';
  };

  const getSystemStatusText = () => {
    if (!systemStats) return 'Загрузка...';
    
    const { market_data } = systemStats;
    const healthySources = Object.values(market_data?.sources || {})
      .filter(source => source.status === 'healthy').length;
    const totalSources = Object.keys(market_data?.sources || {}).length;
    
    return `${healthySources}/${totalSources} источников данных`;
  };

  const renderOverview = () => (
    <Grid container spacing={3}>
      {/* Статус системы */}
      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Статус системы
                </Typography>
                <Typography variant="h6">
                  {getSystemStatusText()}
                </Typography>
              </Box>
              <Chip
                icon={
                  getSystemStatusColor() === 'success' ? <CheckCircleIcon /> :
                  getSystemStatusColor() === 'warning' ? <WarningIcon /> :
                  <ErrorIcon />
                }
                label={
                  getSystemStatusColor() === 'success' ? 'Здорова' :
                  getSystemStatusColor() === 'warning' ? 'Предупреждение' :
                  'Ошибка'
                }
                color={getSystemStatusColor()}
                variant="outlined"
              />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Активные пользователи */}
      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Активные пользователи
                </Typography>
                <Typography variant="h6">
                  {systemStats?.system?.active_users || 0}
                </Typography>
              </Box>
              <PeopleIcon color="primary" />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Версия системы */}
      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Версия
                </Typography>
                <Typography variant="h6">
                  {systemStats?.system?.version || '1.1.0-dev'}
                </Typography>
              </Box>
              <Chip label="DEV" color="info" size="small" />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Последнее обновление */}
      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Обновлено
                </Typography>
                <Typography variant="body2">
                  {lastUpdate ? lastUpdate.toLocaleTimeString() : 'Никогда'}
                </Typography>
              </Box>
              <Tooltip title="Обновить данные">
                <IconButton onClick={fetchSystemStats} disabled={loading}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Быстрые действия */}
      <Grid item xs={12}>
        <Card>
          <CardHeader title="Быстрые действия" />
          <CardContent>
            <Box display="flex" gap={2} flexWrap="wrap">
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={fetchSystemStats}
                disabled={loading}
              >
                Обновить статус
              </Button>
              <Button
                variant="outlined"
                startIcon={<StorageIcon />}
                onClick={() => setCurrentTab(3)}
              >
                Управление промптами
              </Button>
              <Button
                variant="outlined"
                startIcon={<TrendingUpIcon />}
                onClick={() => setCurrentTab(4)}
              >
                Мониторинг данных
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Заголовок */}
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          Админ-панель ChartGenius
        </Typography>
        <Typography variant="subtitle1" color="textSecondary">
          Управление системой анализа криптовалют
        </Typography>
      </Box>

      {/* Ошибки */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          Ошибка загрузки данных: {error}
        </Alert>
      )}

      {/* Загрузка */}
      {loading && !systemStats && (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      )}

      {/* Основной контент */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={currentTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
          >
            {tabs.map((tab, index) => (
              <Tab
                key={index}
                icon={tab.icon}
                label={tab.label}
                iconPosition="start"
              />
            ))}
          </Tabs>
        </Box>

        <TabPanel value={currentTab} index={0}>
          {renderOverview()}
        </TabPanel>

        <TabPanel value={currentTab} index={1}>
          <SystemHealth systemStats={systemStats} onRefresh={fetchSystemStats} />
        </TabPanel>

        <TabPanel value={currentTab} index={2}>
          <UserManager />
        </TabPanel>

        <TabPanel value={currentTab} index={3}>
          <PromptManager />
        </TabPanel>

        <TabPanel value={currentTab} index={4}>
          <MarketDataManager systemStats={systemStats} />
        </TabPanel>

        <TabPanel value={currentTab} index={5}>
          <TaskMonitor />
        </TabPanel>
      </Card>
    </Container>
  );
};

export default AdminDashboard;
