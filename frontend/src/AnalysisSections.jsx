import React, { useState, useEffect, useMemo } from 'react';
import { Box, Typography, Checkbox, FormControlLabel } from '@mui/material';

const TEXT_SECTIONS = [
  { key: 'primary_analysis', title: 'Первичный анализ' },
  { key: 'price_prediction', title: 'Прогноз цены' },
  { key: 'recommendations', title: 'Рекомендации' },
  { key: 'confidence_in_trading_decisions', title: 'Уверенность в решениях' },
];

export default function AnalysisSections({ analysis }) {
  const initialVisibility = useMemo(
    () =>
      TEXT_SECTIONS.reduce((acc, { key }) => {
        acc[key] = true;
        return acc;
      }, {}),
    []
  );

  const [visibility, setVisibility] = useState(initialVisibility);

  useEffect(() => {
    // сбрасываем видимость при получении нового анализа
    setVisibility(initialVisibility);
  }, [analysis, initialVisibility]);

  const toggle = (key) => {
    setVisibility((v) => ({ ...v, [key]: !v[key] }));
  };

  if (!analysis) return null;

  return (
    <Box sx={{ mt: 2, whiteSpace: 'pre-wrap' }}>
      <Box sx={{ mb: 1 }}>
        {TEXT_SECTIONS.map(({ key, title }) => (
          <FormControlLabel
            key={key}
            control={<Checkbox checked={visibility[key]} onChange={() => toggle(key)} />}
            label={title}
          />
        ))}
      </Box>
      {TEXT_SECTIONS.map(({ key, title }) => {
        const val = analysis[key];
        if (!val || !visibility[key]) return null;
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
