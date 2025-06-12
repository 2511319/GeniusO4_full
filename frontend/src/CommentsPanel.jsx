// src/components/CommentsPanel.jsx

import React from 'react';
import PropTypes from 'prop-types';
import { Box, Tabs, Tab, Typography, Divider } from '@mui/material';

/**
 * CommentsPanel отображает два таба:
 * 1. Primary Analysis — тексты глобального/локального тренда, паттернов и аномалий.
 * 2. Explanation — объяснения (explanation) для каждого активного слоя.
 *
 * Props:
 * - analysis: объект с распаршенным JSON-ответом модели.
 * - activeLayers: массив строк — ключи тех слоёв, которые включены пользователем.
 */
export default function CommentsPanel({ analysis, activeLayers }) {
  const [tabIndex, setTabIndex] = React.useState(0);

  const handleTabChange = (event, newValue) => {
    setTabIndex(newValue);
  };

  // Primary analysis and confidence
  const primary = analysis.primary_analysis || {};
  const confidence = analysis.confidence_in_trading_decisions || {};

  return (
    <Box sx={{ width: '100%', bgcolor: 'background.paper', height: '100%', overflowY: 'auto' }}>
      {/* Confidence header */}
      <Box sx={{ p: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          Confidence: {confidence.level || 'N/A'}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          {confidence.reason || ''}
        </Typography>
      </Box>
      <Divider />

      {/* Tabs */}
      <Tabs value={tabIndex} onChange={handleTabChange} aria-label="Comments tabs">
        <Tab label="Primary Analysis" />
        <Tab label="Explanation" />
      </Tabs>

      {/* Primary Analysis Tab */}
      {tabIndex === 0 && (
        <Box sx={{ p: 2 }}>
          {primary.global_trend && (
            <>
              <Typography variant="h6">Global Trend</Typography>
              <Typography variant="body2" paragraph>{primary.global_trend}</Typography>
            </>
          )}
          {primary.local_trend && (
            <>
              <Typography variant="h6">Local Trend</Typography>
              <Typography variant="body2" paragraph>{primary.local_trend}</Typography>
            </>
          )}
          {primary.patterns && (
            <>
              <Typography variant="h6">Patterns</Typography>
              <Typography variant="body2" paragraph>{primary.patterns}</Typography>
            </>
          )}
          {primary.anomalies && (
            <>
              <Typography variant="h6">Anomalies</Typography>
              <Typography variant="body2" paragraph>{primary.anomalies}</Typography>
            </>
          )}
        </Box>
      )}

      {/* Explanation Tab */}
      {tabIndex === 1 && (
        <Box sx={{ p: 2 }}>
          {activeLayers.map((layerKey) => {
            const section = analysis[layerKey];
            const explanation = section?.explanation;
            if (!explanation) return null;

            // Human-readable layer name (e.g. convert snake_case to Title Case)
            const title = layerKey
              .split('_')
              .map(word => word[0].toUpperCase() + word.slice(1))
              .join(' ');

            return (
              <Box key={layerKey} sx={{ mb: 3 }}>
                <Typography variant="h6">{title}</Typography>
                <Typography variant="body2">{explanation}</Typography>
              </Box>
            );
          })}
          {/* Если нет ни одного explanation */}
          {activeLayers.every(key => !analysis[key]?.explanation) && (
            <Typography variant="body2" color="textSecondary">
              No explanations available for the selected indicators.
            </Typography>
          )}
        </Box>
      )}
    </Box>
  );
}

CommentsPanel.propTypes = {
  analysis: PropTypes.object.isRequired,
  activeLayers: PropTypes.arrayOf(PropTypes.string).isRequired,
};
