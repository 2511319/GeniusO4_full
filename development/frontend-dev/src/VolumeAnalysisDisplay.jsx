import React from 'react';
import { Box, Typography, Grid, Card, CardContent, Chip } from '@mui/material';

export default function VolumeAnalysisDisplay({ volumeData }) {
  if (!volumeData) {
    return (
      <Typography variant="body2" color="text.secondary">
        Данные анализа объемов отсутствуют
      </Typography>
    );
  }

  // Если данные переданы как строка, отображаем как есть
  if (typeof volumeData === 'string') {
    return (
      <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
        {volumeData}
      </Typography>
    );
  }

  // Если данные переданы как объект, форматируем их
  if (typeof volumeData === 'object') {
    return (
      <Box>
        {Object.entries(volumeData).map(([key, value]) => (
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
      {JSON.stringify(volumeData, null, 2)}
    </Typography>
  );
}
