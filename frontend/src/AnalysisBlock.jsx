import React from 'react';
import { Box, Typography } from '@mui/material';

const TEXT_SECTIONS = [
  { key: 'primary_analysis', title: 'Первичный анализ' },
  { key: 'recommendations', title: 'Рекомендации' },
  { key: 'price_prediction', title: 'Прогноз цены' },
  { key: 'confidence_in_trading_decisions', title: 'Уверенность в решениях' }
];

export default function AnalysisBlock({ analysis }) {
  if (!analysis) return null;
  return (
    <Box sx={{ mt: 2, whiteSpace: 'pre-wrap' }}>
      {TEXT_SECTIONS.map(({ key, title }) => {
        const val = analysis[key];
        if (!val) return null;
        return (
          <Box key={key} sx={{ mb: 2 }}>
            <Typography variant="h6">{title}</Typography>
            <Typography variant="body2">
              {typeof val === 'string' ? val : JSON.stringify(val, null, 2)}
            </Typography>
          </Box>
        );
      })}
    </Box>
  );
}
