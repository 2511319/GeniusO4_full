import React from 'react';
import {
  Box, Typography, Card, CardContent, Grid, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, List, ListItem, ListItemText, Divider
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import ShowChartIcon from '@mui/icons-material/ShowChart';

export default function TechnicalAnalysisDisplay({ data, type }) {
  if (!data) {
    return (
      <Typography variant="body2" color="text.secondary">
        Данные отсутствуют
      </Typography>
    );
  }

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

  // Отображение уровней поддержки и сопротивления
  if (type === 'support_resistance_levels') {
    const { support_levels = [], resistance_levels = [] } = data;
    
    return (
      <Box>
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Card>
              <CardContent>
                <Typography variant="subtitle1" color="success.main" gutterBottom>
                  Уровни поддержки ({support_levels.length})
                </Typography>
                <List dense>
                  {support_levels.map((level, index) => (
                    <ListItem key={index}>
                      <ListItemText
                        primary={formatPrice(level.price)}
                        secondary={`Сила: ${level.strength || 'N/A'}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={6}>
            <Card>
              <CardContent>
                <Typography variant="subtitle1" color="error.main" gutterBottom>
                  Уровни сопротивления ({resistance_levels.length})
                </Typography>
                <List dense>
                  {resistance_levels.map((level, index) => (
                    <ListItem key={index}>
                      <ListItemText
                        primary={formatPrice(level.price)}
                        secondary={`Сила: ${level.strength || 'N/A'}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  }

  // Отображение линий тренда
  if (type === 'trend_lines') {
    const { lines = [] } = data;
    
    return (
      <Box>
        <Typography variant="subtitle1" gutterBottom>
          Линии тренда ({lines.length})
        </Typography>
        {lines.map((line, index) => (
          <Card key={index} sx={{ mb: 1 }}>
            <CardContent sx={{ py: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {line.type === 'восходящая' ? 
                  <TrendingUpIcon color="success" /> : 
                  <TrendingDownIcon color="error" />
                }
                <Typography variant="body2">
                  {line.type} тренд
                </Typography>
                <Chip 
                  label={`Сила: ${line.strength || 'N/A'}`}
                  size="small"
                  variant="outlined"
                />
              </Box>
              <Typography variant="caption" color="text.secondary">
                {formatDateTime(line.start_point?.date)} - {formatDateTime(line.end_point?.date)}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>
    );
  }

  // Отображение анализа Фибоначчи
  if (type === 'fibonacci_analysis') {
    const { based_on_local_trend, based_on_global_trend } = data;
    
    return (
      <Box>
        {based_on_local_trend && (
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Локальный тренд Фибоначчи
              </Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Уровень</TableCell>
                      <TableCell align="right">Цена</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(based_on_local_trend.levels || {}).map(([level, price]) => (
                      <TableRow key={level}>
                        <TableCell>{level}</TableCell>
                        <TableCell align="right">{formatPrice(price)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        )}
        
        {based_on_global_trend && (
          <Card>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Глобальный тренд Фибоначчи
              </Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Уровень</TableCell>
                      <TableCell align="right">Цена</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(based_on_global_trend.levels || {}).map(([level, price]) => (
                      <TableRow key={level}>
                        <TableCell>{level}</TableCell>
                        <TableCell align="right">{formatPrice(price)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        )}
      </Box>
    );
  }

  // Отображение волн Эллиота
  if (type === 'elliott_wave_analysis') {
    const { waves = [] } = data;
    
    return (
      <Box>
        <Typography variant="subtitle1" gutterBottom>
          Волны Эллиота ({waves.length})
        </Typography>
        {waves.map((wave, index) => (
          <Card key={index} sx={{ mb: 1 }}>
            <CardContent sx={{ py: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <ShowChartIcon color="primary" />
                <Typography variant="body2">
                  Волна {wave.wave_number}
                </Typography>
                <Chip 
                  label={wave.type || 'N/A'}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              </Box>
              <Typography variant="caption" color="text.secondary">
                {formatPrice(wave.start_point?.price)} → {formatPrice(wave.end_point?.price)}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>
    );
  }

  // Отображение дивергенций
  if (type === 'divergence_analysis' && Array.isArray(data)) {
    return (
      <Box>
        <Typography variant="subtitle1" gutterBottom>
          Дивергенции ({data.length})
        </Typography>
        {data.map((div, index) => (
          <Card key={index} sx={{ mb: 1 }}>
            <CardContent sx={{ py: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {div.type === 'bullish' ? 
                  <TrendingUpIcon color="success" /> : 
                  <TrendingDownIcon color="error" />
                }
                <Typography variant="body2">
                  {div.indicator} - {div.type}
                </Typography>
              </Box>
              <Typography variant="caption" color="text.secondary">
                {formatDateTime(div.date)}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>
    );
  }

  // Общий формат для остальных типов
  return (
    <Box>
      <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
        {typeof data === 'string' ? data : JSON.stringify(data, null, 2)}
      </Typography>
    </Box>
  );
}
