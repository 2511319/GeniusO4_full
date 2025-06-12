// src/components/CommentsPanel.jsx

import React from 'react';
import PropTypes from 'prop-types';
import { Box, Tabs, Tab, Typography, Divider } from '@mui/material';

/**
 * Панель комментариев
 * - Tab 1: Primary Analysis
 * - Tab 2: Explanation (explanation для activeLayers)
 */
export default function CommentsPanel({ analysis, activeLayers }) {
  const [tab, setTab] = React.useState(0);

  const handleChange = (e, newVal) => setTab(newVal);

  const primary = analysis.primary_analysis || {};
  const conf    = analysis.confidence_in_trading_decisions || {};

  return (
    <Box
      sx={{
        position: 'absolute',
        top: 0,
        right: 0,
        width: 300,
        height: '100%',
        bgcolor: '#f5f5f5',
        overflowY: 'auto',
        p: 1,
      }}
    >
      <Typography variant="subtitle2">Confidence: {conf.level || 'N/A'}</Typography>
      <Typography variant="body2" color="textSecondary">{conf.reason}</Typography>
      <Divider sx={{ my: 1 }} />

      <Tabs value={tab} onChange={handleChange}>
        <Tab label="Primary Analysis" />
        <Tab label="Explanation" />
      </Tabs>

      {tab === 0 && (
        <Box sx={{ mt: 1 }}>
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

      {tab === 1 && (
        <Box sx={{ mt: 1 }}>
          {activeLayers.map((layer) => {
            const expl = analysis[layer]?.explanation;
            if (!expl) return null;
            const title = layer
              .split('_')
              .map(w => w[0].toUpperCase() + w.slice(1))
              .join(' ');
            return (
              <Box key={layer} sx={{ mb: 2 }}>
                <Typography variant="h6">{title}</Typography>
                <Typography variant="body2">{expl}</Typography>
              </Box>
            );
          })}
          {activeLayers.every(l => !analysis[l]?.explanation) && (
            <Typography variant="body2" color="textSecondary">
              No explanations for selected indicators.
            </Typography>
          )}
        </Box>
      )}
    </Box>
  );
}

CommentsPanel.propTypes = {
  analysis:     PropTypes.object.isRequired,
  activeLayers: PropTypes.arrayOf(PropTypes.string).isRequired,
};
