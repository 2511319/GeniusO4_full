// 📊 Market Data Manager Component for ChartGenius Admin
// Версия: 1.1.0-dev
// Управление источниками рыночных данных

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardHeader,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  IconButton,
  Tooltip,
  Alert,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Storage as StorageIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Search as SearchIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';

const MarketDataManager = ({ systemStats }) => {
  const [exchanges, setExchanges] = useState({});
  const [symbols, setSymbols] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedExchange, setSelectedExchange] = useState(null);
  const [symbolsDialog, setSymbolsDialog] = useState(false);
  const [tickerDialog, setTickerDialog] = useState(false);
  const [tickerData, setTickerData] = useState(null);
  const [testSymbol, setTestSymbol] = useState('BTC/USDT');

  const fetchExchanges = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/market/exchanges');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.success) {
        setExchanges(data.exchanges);
      }

    } catch (err) {
      console.error('Error fetching exchanges:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchSymbols = async (exchange) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/market/symbols/${exchange}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.success) {
        setSymbols(data.symbols);
        setSelectedExchange(exchange);
        setSymbolsDialog(true);
      }

    } catch (err) {
      console.error('Error fetching symbols:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchTicker = async (symbol) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/market/ticker/${encodeURIComponent(symbol)}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.success) {
        setTickerData(data.ticker);
        setTickerDialog(true);
      }

    } catch (err) {
      console.error('Error fetching ticker:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExchanges();
  }, []);

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

  const renderDataSources = () => {
    const sources = systemStats?.market_data?.sources || {};
    
    return (
      <Card>
        <CardHeader
          title={
            <Box display="flex" alignItems="center" gap={1}>
              <TrendingUpIcon />
              <Typography variant="h6">Источники данных</Typography>
            </Box>
          }
          action={
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={fetchExchanges}
              disabled={loading}
            >
              Обновить
            </Button>
          }
        />
        <CardContent>
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Источник</TableCell>
                  <TableCell>Статус</TableCell>
                  <TableCell>Время ответа</TableCell>
                  <TableCell>Последняя проверка</TableCell>
                  <TableCell>Действия</TableCell>
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
                      {sourceName.startsWith('ccxt_') && (
                        <Tooltip title="Просмотреть символы">
                          <IconButton
                            size="small"
                            onClick={() => fetchSymbols(sourceName)}
                          >
                            <VisibilityIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    );
  };

  const renderExchanges = () => {
    const ccxtExchanges = systemStats?.ccxt_exchanges || {};
    
    return (
      <Card>
        <CardHeader
          title={
            <Box display="flex" alignItems="center" gap={1}>
              <StorageIcon />
              <Typography variant="h6">CCXT Биржи</Typography>
            </Box>
          }
        />
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
                  <TableCell>Действия</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.entries(ccxtExchanges).map(([exchangeName, exchangeData]) => (
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
                      {exchangeData.error_rate ? 
                        `${(exchangeData.error_rate * 100).toFixed(1)}%` : 
                        '0%'
                      }
                    </TableCell>
                    <TableCell>
                      <Tooltip title="Просмотреть символы">
                        <IconButton
                          size="small"
                          onClick={() => fetchSymbols(`ccxt_${exchangeName}`)}
                        >
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    );
  };

  return (
    <Box>
      {/* Заголовок */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" component="h2">
          Управление рыночными данными
        </Typography>
        <Button
          variant="contained"
          startIcon={<SearchIcon />}
          onClick={() => fetchTicker(testSymbol)}
        >
          Тест тикера
        </Button>
      </Box>

      {/* Ошибки */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Загрузка */}
      {loading && (
        <LinearProgress sx={{ mb: 2 }} />
      )}

      {/* Компоненты */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          {renderDataSources()}
        </Grid>
        
        <Grid item xs={12}>
          {renderExchanges()}
        </Grid>
      </Grid>

      {/* Диалог символов */}
      <Dialog
        open={symbolsDialog}
        onClose={() => setSymbolsDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Символы биржи: {selectedExchange}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="textSecondary" gutterBottom>
            Найдено символов: {symbols.length}
          </Typography>
          <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
            {symbols.slice(0, 50).map((symbol, index) => (
              <Chip
                key={index}
                label={symbol}
                size="small"
                sx={{ m: 0.5 }}
                onClick={() => fetchTicker(symbol)}
              />
            ))}
            {symbols.length > 50 && (
              <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                ... и еще {symbols.length - 50} символов
              </Typography>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSymbolsDialog(false)}>
            Закрыть
          </Button>
        </DialogActions>
      </Dialog>

      {/* Диалог тикера */}
      <Dialog
        open={tickerDialog}
        onClose={() => setTickerDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Данные тикера
        </DialogTitle>
        <DialogContent>
          {tickerData && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {tickerData.symbol}
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Цена
                  </Typography>
                  <Typography variant="h6">
                    ${tickerData.last?.toFixed(2)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Изменение
                  </Typography>
                  <Typography 
                    variant="h6" 
                    color={tickerData.percentage > 0 ? 'success.main' : 'error.main'}
                  >
                    {tickerData.percentage?.toFixed(2)}%
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Объем
                  </Typography>
                  <Typography variant="body1">
                    {tickerData.volume?.toFixed(2)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Источник
                  </Typography>
                  <Typography variant="body1">
                    {tickerData.source}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <TextField
            size="small"
            value={testSymbol}
            onChange={(e) => setTestSymbol(e.target.value)}
            placeholder="BTC/USDT"
            sx={{ mr: 2 }}
          />
          <Button onClick={() => fetchTicker(testSymbol)}>
            Тест
          </Button>
          <Button onClick={() => setTickerDialog(false)}>
            Закрыть
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MarketDataManager;
