// 🏥 System Health Component for ChartGenius Admin
// Версия: 1.1.0-dev
// Мониторинг состояния системы

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  Button,
  IconButton,
  Tooltip,
  Collapse
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Storage as StorageIcon,
  TrendingUp as TrendingUpIcon,
  Memory as MemoryIcon,
  Speed as SpeedIcon
} from '@mui/icons-material';

const SystemHealth = ({ systemStats, onRefresh }) => {
  const [expandedSections, setExpandedSections] = useState({
    dataSources: true,
    exchanges: false,
    system: false
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircleIcon color="success" />;
      case 'degraded':
        return <WarningIcon color="warning" />;
      case 'unhealthy':
      case 'unavailable':
        return <ErrorIcon color="error" />;
      default:
        return <WarningIcon color="disabled" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'success';
      case 'degraded':
        return 'warning';
      case 'unhealthy':
      case 'unavailable':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatResponseTime = (time) => {
    if (typeof time !== 'number') return 'N/A';
    return `${(time * 1000).toFixed(0)}ms`;
  };

  const formatErrorRate = (rate) => {
    if (typeof rate !== 'number') return 'N/A';
    return `${(rate * 100).toFixed(1)}%`;
  };

  const renderDataSourcesHealth = () => {
    const sources = systemStats?.market_data?.sources || {};
    
    return (
      <Card>
        <CardHeader
          title={
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box display="flex" alignItems="center" gap={1}>
                <TrendingUpIcon />
                <Typography variant="h6">Источники данных</Typography>
              </Box>
              <IconButton onClick={() => toggleSection('dataSources')}>
                {expandedSections.dataSources ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            </Box>
          }
        />
        <Collapse in={expandedSections.dataSources}>
          <CardContent>
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Источник</TableCell>
                    <TableCell>Статус</TableCell>
                    <TableCell>Время ответа</TableCell>
                    <TableCell>Последняя проверка</TableCell>
                    <TableCell>Ошибка</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(sources).map(([sourceName, sourceData]) => (
                    <TableRow key={sourceName}>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          {getStatusIcon(sourceData.status)}
                          <Typography variant="body2" fontWeight="medium">
                            {sourceName}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={sourceData.status}
                          color={getStatusColor(sourceData.status)}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        {formatResponseTime(sourceData.response_time)}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="textSecondary">
                          {sourceData.last_check ? 
                            new Date(sourceData.last_check).toLocaleTimeString() : 
                            'N/A'
                          }
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {sourceData.error && (
                          <Tooltip title={sourceData.error}>
                            <Chip
                              label="Ошибка"
                              color="error"
                              size="small"
                              variant="outlined"
                            />
                          </Tooltip>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Collapse>
      </Card>
    );
  };

  const renderExchangesHealth = () => {
    const exchanges = systemStats?.ccxt_exchanges || {};
    
    return (
      <Card>
        <CardHeader
          title={
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box display="flex" alignItems="center" gap={1}>
                <StorageIcon />
                <Typography variant="h6">CCXT Биржи</Typography>
              </Box>
              <IconButton onClick={() => toggleSection('exchanges')}>
                {expandedSections.exchanges ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            </Box>
          }
        />
        <Collapse in={expandedSections.exchanges}>
          <CardContent>
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Биржа</TableCell>
                    <TableCell>Статус</TableCell>
                    <TableCell>Приоритет</TableCell>
                    <TableCell>Время ответа</TableCell>
                    <TableCell>Ошибки</TableCell>
                    <TableCell>Включена</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(exchanges).map(([exchangeName, exchangeData]) => (
                    <TableRow key={exchangeName}>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          {getStatusIcon(exchangeData.status)}
                          <Typography variant="body2" fontWeight="medium">
                            {exchangeName}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={exchangeData.status}
                          color={getStatusColor(exchangeData.status)}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={`#${exchangeData.priority}`}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        {formatResponseTime(exchangeData.response_time)}
                      </TableCell>
                      <TableCell>
                        {formatErrorRate(exchangeData.error_rate)}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={exchangeData.enabled ? 'Да' : 'Нет'}
                          color={exchangeData.enabled ? 'success' : 'default'}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Collapse>
      </Card>
    );
  };

  const renderSystemMetrics = () => {
    const system = systemStats?.system || {};
    
    return (
      <Card>
        <CardHeader
          title={
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box display="flex" alignItems="center" gap={1}>
                <MemoryIcon />
                <Typography variant="h6">Системные метрики</Typography>
              </Box>
              <IconButton onClick={() => toggleSection('system')}>
                {expandedSections.system ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            </Box>
          }
        />
        <Collapse in={expandedSections.system}>
          <CardContent>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Версия системы
                  </Typography>
                  <Typography variant="h6">
                    {system.version || '1.1.0-dev'}
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Среда
                  </Typography>
                  <Chip
                    label={system.environment || 'development'}
                    color="info"
                    variant="outlined"
                  />
                </Box>
              </Grid>

              <Grid item xs={12} md={6}>
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Сервисы
                  </Typography>
                  {system.services && Object.entries(system.services).map(([service, status]) => (
                    <Box key={service} display="flex" alignItems="center" gap={1} mb={1}>
                      {getStatusIcon(status)}
                      <Typography variant="body2">
                        {service}: {status}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </Grid>

              <Grid item xs={12} md={6}>
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Последнее обновление
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {system.timestamp ? 
                      new Date(system.timestamp).toLocaleString() : 
                      'N/A'
                    }
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Collapse>
      </Card>
    );
  };

  if (!systemStats) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
        <Typography variant="h6" color="textSecondary">
          Нет данных о состоянии системы
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Заголовок с кнопкой обновления */}
      <Box display="flex" justifyContent="between" alignItems="center" mb={3}>
        <Typography variant="h5" component="h2">
          Состояние системы
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={onRefresh}
        >
          Обновить
        </Button>
      </Box>

      {/* Общий статус */}
      <Alert 
        severity={
          Object.values(systemStats?.market_data?.sources || {})
            .every(source => source.status === 'healthy') ? 'success' : 'warning'
        }
        sx={{ mb: 3 }}
      >
        <Typography variant="body1">
          Система работает. Мониторинг {Object.keys(systemStats?.market_data?.sources || {}).length} источников данных
          и {Object.keys(systemStats?.ccxt_exchanges || {}).length} бирж.
        </Typography>
      </Alert>

      {/* Компоненты здоровья */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          {renderDataSourcesHealth()}
        </Grid>
        
        <Grid item xs={12}>
          {renderExchangesHealth()}
        </Grid>
        
        <Grid item xs={12}>
          {renderSystemMetrics()}
        </Grid>
      </Grid>
    </Box>
  );
};

export default SystemHealth;
