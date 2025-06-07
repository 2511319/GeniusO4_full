import React from 'react';
import {
  Accordion, AccordionSummary, AccordionDetails,
  Typography, Box,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const SECTIONS = [
  { key: 'primary_analysis',                 title: 'Первичный анализ' },
  { key: 'price_prediction',                 title: 'Прогноз цены' },
  { key: 'recommendations',                  title: 'Рекомендации' },
  { key: 'confidence_in_trading_decisions',  title: 'Уверенность в решениях' },
];

export default function AnalysisSections({ analysis }) {
  if (!analysis) return null;

  return (
    <Box sx={{ width: '100%' }}>
      {SECTIONS.map(({ key, title }) => {
        const value = analysis[key];
        if (!value) return null;

        return (
          <Accordion key={key} defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">{title}</Typography>
            </AccordionSummary>

            <AccordionDetails sx={{ whiteSpace: 'pre-wrap' }}>
              <Typography variant="body2">
                {typeof value === 'string'
                  ? value
                  : JSON.stringify(value, null, 2)}
              </Typography>
            </AccordionDetails>
          </Accordion>
        );
      })}
    </Box>
  );
}

