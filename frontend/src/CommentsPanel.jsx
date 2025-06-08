import React, { useState, useMemo } from 'react';
import {
  Box, Tabs, Tab, TextField, Typography
} from '@mui/material';

function a11yProps(index) {
  return {
    id: `comments-tab-${index}`,
    'aria-controls': `comments-tabpanel-${index}`,
  };
}

export default function CommentsPanel({ analysis, layers = [] }) {
  const [value, setValue] = useState(0);

  const primary = analysis?.primary_analysis || {};

  const explanations = useMemo(() => {
    if (!analysis) return [];
    const result = [];
    layers.forEach((layer) => {
      let text = '';
      if (analysis[layer]) {
        const val = analysis[layer];
        text = typeof val === 'string' ? val : JSON.stringify(val, null, 2);
      } else if (analysis.indicators_analysis && analysis.indicators_analysis[layer]) {
        const obj = analysis.indicators_analysis[layer];
        if (typeof obj === 'string') text = obj;
        else {
          text = Object.entries(obj)
            .map(([k, v]) => `${k}: ${v}`)
            .join('\n');
        }
      }
      if (text) {
        result.push({ title: layer, text });
      }
    });
    return result;
  }, [analysis, layers]);

  return (
    <Box sx={{ width: '100%' }}>
      <Tabs value={value} onChange={(e, val) => setValue(val)} aria-label="comments tabs">
        <Tab label="Primary" {...a11yProps(0)} />
        <Tab label="Explanation" {...a11yProps(1)} />
      </Tabs>
      {value === 0 && (
        <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
          <TextField
            label="Глобальный тренд"
            multiline
            minRows={2}
            value={primary.global_trend || ''}
            InputProps={{ readOnly: true }}
          />
          <TextField
            label="Локальный тренд"
            multiline
            minRows={2}
            value={primary.local_trend || ''}
            InputProps={{ readOnly: true }}
          />
          <TextField
            label="Паттерны"
            multiline
            minRows={2}
            value={primary.patterns || ''}
            InputProps={{ readOnly: true }}
          />
          <TextField
            label="Аномалии"
            multiline
            minRows={2}
            value={primary.anomalies || ''}
            InputProps={{ readOnly: true }}
          />
        </Box>
      )}
      {value === 1 && (
        <Box sx={{ p: 2 }}>
          {explanations.map((item) => (
            <Box key={item.title} sx={{ mb: 2, whiteSpace: 'pre-wrap' }}>
              <Typography variant="subtitle1">{item.title}</Typography>
              <Typography variant="body2">{item.text}</Typography>
            </Box>
          ))}
        </Box>
      )}
    </Box>
  );
}
