import React from 'react';
import {
  Box, Typography, Card, CardContent, Chip, Grid,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, Divider
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import ShowChartIcon from '@mui/icons-material/ShowChart';

export default function RecommendationsDisplay({ recommendations }) {
  if (!recommendations || !recommendations.trading_strategies) {
    return (
      <Typography variant="body2" color="text.secondary">
        Торговые рекомендации отсутствуют
      </Typography>
    );
  }

  const strategies = recommendations.trading_strategies;

  const getStrategyIcon = (strategy) => {
    const strategyText = strategy.strategy?.toLowerCase() || '';
    if (strategyText.includes('нисходящ') || strategyText.includes('short') || strategyText.includes('продаж')) {
      return <TrendingDownIcon color="error" />;
    }
    if (strategyText.includes('восходящ') || strategyText.includes('long') || strategyText.includes('покуп')) {
      return <TrendingUpIcon color="success" />;
    }
    return <ShowChartIcon color="primary" />;
  };

  const getStrategyColor = (strategy) => {
    const strategyText = strategy.strategy?.toLowerCase() || '';
    if (strategyText.includes('нисходящ') || strategyText.includes('short') || strategyText.includes('продаж')) {
      return 'error';
    }
    if (strategyText.includes('восходящ') || strategyText.includes('long') || strategyText.includes('покуп')) {
      return 'success';
    }
    return 'primary';
  };

  const getRiskColor = (risk) => {
    const riskText = risk?.toLowerCase() || '';
    if (riskText.includes('высок') || riskText.includes('high')) return 'error';
    if (riskText.includes('средн') || riskText.includes('умерен') || riskText.includes('medium')) return 'warning';
    if (riskText.includes('низк') || riskText.includes('low')) return 'success';
    return 'default';
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Торговые стратегии ({strategies.length})
      </Typography>
      
      {strategies.map((strategy, index) => (
        <Card key={index} sx={{ mb: 2, border: 1, borderColor: 'divider' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              {getStrategyIcon(strategy)}
              <Typography variant="subtitle1" sx={{ ml: 1, fontWeight: 'bold' }}>
                Стратегия #{index + 1}
              </Typography>
              <Chip 
                label={getStrategyColor(strategy)} 
                color={getStrategyColor(strategy)}
                size="small" 
                sx={{ ml: 'auto' }}
              />
            </Box>

            <Typography variant="body2" sx={{ mb: 2 }}>
              {strategy.strategy}
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Box sx={{ p: 1, bgcolor: 'success.light', borderRadius: 1 }}>
                  <Typography variant="caption" color="success.contrastText">
                    Точка входа
                  </Typography>
                  <Typography variant="body2" fontWeight="bold" color="success.contrastText">
                    ${strategy.entry_point?.Price?.toLocaleString()}
                  </Typography>
                  <Typography variant="caption" color="success.contrastText">
                    {strategy.entry_point?.Date}
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={6}>
                <Box sx={{ p: 1, bgcolor: 'error.light', borderRadius: 1 }}>
                  <Typography variant="caption" color="error.contrastText">
                    Точка выхода
                  </Typography>
                  <Typography variant="body2" fontWeight="bold" color="error.contrastText">
                    ${strategy.exit_point?.Price?.toLocaleString()}
                  </Typography>
                  <Typography variant="caption" color="error.contrastText">
                    {strategy.exit_point?.Date}
                  </Typography>
                </Box>
              </Grid>
            </Grid>

            <Divider sx={{ my: 2 }} />

            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Параметр</TableCell>
                    <TableCell align="right">Значение</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell>Стоп-лосс</TableCell>
                    <TableCell align="right">
                      <Typography color="error.main" fontWeight="bold">
                        ${strategy.stop_loss?.toLocaleString()}
                      </Typography>
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Тейк-профит</TableCell>
                    <TableCell align="right">
                      <Typography color="success.main" fontWeight="bold">
                        ${strategy.take_profit?.toLocaleString()}
                      </Typography>
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Риск</TableCell>
                    <TableCell align="right">
                      <Chip 
                        label={strategy.risk} 
                        color={getRiskColor(strategy.risk)}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Потенциальная прибыль</TableCell>
                    <TableCell align="right">
                      <Typography color="success.main">
                        {strategy.profit}
                      </Typography>
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>

            {strategy.other_details && (
              <Box sx={{ mt: 2, p: 1, bgcolor: 'background.default', borderRadius: 1, border: '1px solid', borderColor: 'divider' }}>
                <Typography variant="caption" color="text.secondary">
                  Дополнительные детали:
                </Typography>
                <Typography variant="body2">
                  {strategy.other_details}
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>
      ))}
    </Box>
  );
}
