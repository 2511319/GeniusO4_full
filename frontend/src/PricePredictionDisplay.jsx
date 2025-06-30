import React from 'react';
import {
  Box, Typography, Card, CardContent, Table, TableBody, 
  TableCell, TableContainer, TableHead, TableRow, Paper,
  Chip, LinearProgress
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';

export default function PricePredictionDisplay({ prediction }) {
  if (!prediction) {
    return (
      <Typography variant="body2" color="text.secondary">
        Прогноз цены отсутствует
      </Typography>
    );
  }

  const { forecast, virtual_candles } = prediction;

  const calculateTrend = (candles) => {
    if (!candles || candles.length < 2) return { direction: 'neutral', change: 0 };
    
    const firstPrice = candles[0].close;
    const lastPrice = candles[candles.length - 1].close;
    const change = ((lastPrice - firstPrice) / firstPrice) * 100;
    
    return {
      direction: change > 0 ? 'up' : change < 0 ? 'down' : 'neutral',
      change: Math.abs(change)
    };
  };

  const trend = calculateTrend(virtual_candles);

  const getTrendIcon = (direction) => {
    switch (direction) {
      case 'up': return <TrendingUpIcon color="success" />;
      case 'down': return <TrendingDownIcon color="error" />;
      default: return null;
    }
  };

  const getTrendColor = (direction) => {
    switch (direction) {
      case 'up': return 'success';
      case 'down': return 'error';
      default: return 'default';
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price);
  };

  const formatDateTime = (dateStr) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleString('ru-RU', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Прогноз цены на 24 часа
      </Typography>

      {/* Общий прогноз */}
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            {getTrendIcon(trend.direction)}
            <Typography variant="subtitle1" sx={{ ml: 1 }}>
              Общий тренд
            </Typography>
            <Chip 
              label={`${trend.change.toFixed(2)}%`}
              color={getTrendColor(trend.direction)}
              size="small"
              sx={{ ml: 'auto' }}
            />
          </Box>
          
          <Typography variant="body2" sx={{ mb: 2 }}>
            {forecast}
          </Typography>

          {virtual_candles && virtual_candles.length > 0 && (
            <Box>
              <Typography variant="caption" color="text.secondary">
                Прогнозируемый диапазон:
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                <Box>
                  <Typography variant="caption">Начальная цена</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {formatPrice(virtual_candles[0].open)}
                  </Typography>
                </Box>
                <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="caption">Конечная цена</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {formatPrice(virtual_candles[virtual_candles.length - 1].close)}
                  </Typography>
                </Box>
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Детальный прогноз по свечам */}
      {virtual_candles && virtual_candles.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="subtitle1" gutterBottom>
              Детальный прогноз ({virtual_candles.length} свечей)
            </Typography>
            
            <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 300 }}>
              <Table size="small" stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell>Время</TableCell>
                    <TableCell align="right">Открытие</TableCell>
                    <TableCell align="right">Максимум</TableCell>
                    <TableCell align="right">Минимум</TableCell>
                    <TableCell align="right">Закрытие</TableCell>
                    <TableCell align="center">Тренд</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {virtual_candles.map((candle, index) => {
                    const candleTrend = candle.close > candle.open ? 'up' : 
                                       candle.close < candle.open ? 'down' : 'neutral';
                    const changePercent = ((candle.close - candle.open) / candle.open) * 100;
                    
                    return (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="caption">
                            {formatDateTime(candle.date)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2">
                            {formatPrice(candle.open)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" color="success.main">
                            {formatPrice(candle.high)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" color="error.main">
                            {formatPrice(candle.low)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography 
                            variant="body2" 
                            fontWeight="bold"
                            color={candleTrend === 'up' ? 'success.main' : 
                                   candleTrend === 'down' ? 'error.main' : 'text.primary'}
                          >
                            {formatPrice(candle.close)}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            label={`${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(2)}%`}
                            color={getTrendColor(candleTrend)}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}
