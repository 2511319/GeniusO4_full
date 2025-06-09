import React, { useState, useEffect } from 'react';
import {
  Box, Tabs, Tab, TextField, Typography
} from '@mui/material';

function a11yProps(index) {
  return {
    id: `comments-tab-${index}`,
    'aria-controls': `comments-tabpanel-${index}`,
  };
}

export default function CommentsPanel({ analysis, explanations = [], layers = [] }) {
  const [value, setValue] = useState(0);
  const [layerExplanations, setLayerExplanations] = useState([]);

  const primary = analysis?.primary_analysis || {};

  useEffect(() => {
    if (!Array.isArray(layers)) return;

    const items = layers
      .map((layer) => {
        const fromAnalysis = analysis?.[layer]?.explanation;
        const fromProps = explanations.find((ex) => ex.key === layer);
        const fallback = fromProps ? fromProps['Текст'] || fromProps.explanation : undefined;
        const explanation = fromAnalysis || fallback;
        return explanation ? { layerName: layer, explanation } : null;
      })
      .filter(Boolean);

    setLayerExplanations(items);
  }, [analysis, layers, explanations]);

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
          {layerExplanations.map((item) => (
            <Box key={item.layerName} sx={{ mb: 2, whiteSpace: 'pre-wrap' }}>
              <Typography variant="subtitle1">{item.layerName}</Typography>
              <Typography variant="body2">{item.explanation}</Typography>
            </Box>
          ))}
        </Box>
      )}
    </Box>
  );
}
