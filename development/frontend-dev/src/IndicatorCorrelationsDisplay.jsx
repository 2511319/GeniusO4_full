import React from 'react';
import { Box, Typography, Grid, Card, CardContent, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';

export default function IndicatorCorrelationsDisplay({ correlations }) {
  if (!correlations) {
    return (
      <Typography variant="body2" color="text.secondary">
        Данные корреляций индикаторов отсутствуют
      </Typography>
    );
  }

  // Если данные переданы как строка, отображаем как есть
  if (typeof correlations === 'string') {
    return (
      <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
        {correlations}
      </Typography>
    );
  }

  // Если данные переданы как массив корреляций
  if (Array.isArray(correlations)) {
    return (
      <Box>
        {correlations.map((correlation, index) => (
          <Card key={index} sx={{ mb: 1, bgcolor: 'grey.50' }}>
            <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={6}>
                  <Typography variant="body2" fontWeight="bold">
                    {correlation.pair || `Корреляция ${index + 1}`}
                  </Typography>
                </Grid>
                <Grid item xs={3}>
                  <Chip 
                    label={correlation.value || correlation.correlation || 'N/A'} 
                    size="small" 
                    color={
                      Math.abs(parseFloat(correlation.value || correlation.correlation || 0)) > 0.7 
                        ? 'error' 
                        : Math.abs(parseFloat(correlation.value || correlation.correlation || 0)) > 0.3 
                        ? 'warning' 
                        : 'success'
                    }
                  />
                </Grid>
                <Grid item xs={3}>
                  <Typography variant="caption" color="text.secondary">
                    {correlation.strength || 'Умеренная'}
                  </Typography>
                </Grid>
              </Grid>
              {correlation.description && (
                <Typography variant="caption" sx={{ mt: 1, display: 'block' }}>
                  {correlation.description}
                </Typography>
              )}
            </CardContent>
          </Card>
        ))}
      </Box>
    );
  }

  // Если данные переданы как объект, форматируем их
  if (typeof correlations === 'object') {
    return (
      <Box>
        {Object.entries(correlations).map(([key, value]) => (
          <Card key={key} sx={{ mb: 1, bgcolor: 'grey.50' }}>
            <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
              <Typography variant="subtitle2" color="primary" gutterBottom>
                {key.replace(/_/g, ' ').toUpperCase()}
              </Typography>
              <Typography variant="body2">
                {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>
    );
  }

  return (
    <Typography variant="body2">
      {JSON.stringify(correlations, null, 2)}
    </Typography>
  );
}
