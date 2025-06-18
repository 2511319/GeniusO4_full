import React from 'react';
import {
  Box, Typography, Card, CardContent, Grid, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, LinearProgress
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import TrendingFlatIcon from '@mui/icons-material/TrendingFlat';

export default function IndicatorsAnalysisDisplay({ indicators }) {
  if (!indicators || typeof indicators !== 'object') {
    return (
      <Typography variant="body2" color="text.secondary">
        Анализ индикаторов отсутствует
      </Typography>
    );
  }

  const getTrendIcon = (trend) => {
    const trendText = trend?.toLowerCase() || '';
    if (trendText.includes('бычий') || trendText.includes('восходящ') || trendText.includes('bullish')) {
      return <TrendingUpIcon color="success" />;
    }
    if (trendText.includes('медвежий') || trendText.includes('нисходящ') || trendText.includes('bearish')) {
      return <TrendingDownIcon color="error" />;
    }
    return <TrendingFlatIcon color="primary" />;
  };

  const getTrendColor = (trend) => {
    const trendText = trend?.toLowerCase() || '';
    if (trendText.includes('бычий') || trendText.includes('восходящ') || trendText.includes('bullish')) {
      return 'success';
    }
    if (trendText.includes('медвежий') || trendText.includes('нисходящ') || trendText.includes('bearish')) {
      return 'error';
    }
    return 'primary';
  };

  const formatValue = (value) => {
    if (typeof value === 'number') {
      return value.toLocaleString('ru-RU', { maximumFractionDigits: 2 });
    }
    return String(value);
  };

  const getIndicatorProgress = (indicator, value) => {
    // Для RSI и Stochastic Oscillator показываем прогресс-бар
    if (indicator === 'RSI' || indicator === 'Stochastic_Oscillator') {
      const numValue = typeof value === 'number' ? value : parseFloat(value) || 0;
      const progress = Math.min(Math.max(numValue, 0), 100);
      let color = 'primary';
      
      if (numValue > 70) color = 'error';
      else if (numValue < 30) color = 'success';
      else if (numValue >= 30 && numValue <= 70) color = 'warning';
      
      return (
        <Box sx={{ width: '100%', mt: 1 }}>
          <LinearProgress 
            variant="determinate" 
            value={progress} 
            color={color}
            sx={{ height: 8, borderRadius: 4 }}
          />
          <Typography variant="caption" color="text.secondary">
            {progress.toFixed(1)}%
          </Typography>
        </Box>
      );
    }
    return null;
  };

  const renderIndicatorCard = (name, data) => {
    const displayName = name.replace(/_/g, ' ').toUpperCase();
    
    return (
      <Card key={name} sx={{ height: '100%' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            {getTrendIcon(data.trend)}
            <Typography variant="h6" sx={{ ml: 1 }}>
              {displayName}
            </Typography>
            <Chip 
              label={data.trend || 'N/A'}
              color={getTrendColor(data.trend)}
              size="small"
              sx={{ ml: 'auto' }}
            />
          </Box>

          {/* Основное значение */}
          {data.current_value !== undefined && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Текущее значение:
              </Typography>
              <Typography variant="h5" fontWeight="bold">
                {formatValue(data.current_value)}
              </Typography>
              {getIndicatorProgress(name, data.current_value)}
            </Box>
          )}

          {/* Дополнительные значения для MACD */}
          {name === 'MACD' && (
            <TableContainer component={Paper} variant="outlined" sx={{ mb: 2 }}>
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell>Signal</TableCell>
                    <TableCell align="right">{formatValue(data.signal)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Histogram</TableCell>
                    <TableCell align="right">{formatValue(data.histogram)}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {/* Дополнительные значения для Bollinger Bands */}
          {name === 'Bollinger_Bands' && (
            <TableContainer component={Paper} variant="outlined" sx={{ mb: 2 }}>
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell>Верхняя полоса</TableCell>
                    <TableCell align="right">{formatValue(data.upper_band)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Средняя полоса</TableCell>
                    <TableCell align="right">{formatValue(data.middle_band)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Нижняя полоса</TableCell>
                    <TableCell align="right">{formatValue(data.lower_band)}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {/* Дополнительные значения для Ichimoku Cloud */}
          {name === 'Ichimoku_Cloud' && (
            <TableContainer component={Paper} variant="outlined" sx={{ mb: 2 }}>
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell>Ichimoku A</TableCell>
                    <TableCell align="right">{formatValue(data.ichimoku_a)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Ichimoku B</TableCell>
                    <TableCell align="right">{formatValue(data.ichimoku_b)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Base Line</TableCell>
                    <TableCell align="right">{formatValue(data.base_line)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Conversion Line</TableCell>
                    <TableCell align="right">{formatValue(data.conversion_line)}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {/* Дополнительные значения для Moving Average Envelopes */}
          {name === 'Moving_Average_Envelopes' && (
            <TableContainer component={Paper} variant="outlined" sx={{ mb: 2 }}>
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell>Верхняя граница</TableCell>
                    <TableCell align="right">{formatValue(data.upper_envelope)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Нижняя граница</TableCell>
                    <TableCell align="right">{formatValue(data.lower_envelope)}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {/* Комментарий */}
          {data.comment && (
            <Box sx={{ p: 1, bgcolor: 'grey.100', borderRadius: 1 }}>
              <Typography variant="body2">
                {data.comment}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Анализ индикаторов ({Object.keys(indicators).length})
      </Typography>
      
      <Grid container spacing={2}>
        {Object.entries(indicators).map(([name, data]) => (
          <Grid item xs={12} sm={6} md={4} key={name}>
            {renderIndicatorCard(name, data)}
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
