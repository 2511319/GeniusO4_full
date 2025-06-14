// src/components/InsightsPanel.jsx

import React from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';
import { Box, Typography, Divider } from '@mui/material';

/**
 * Панель Insights для прочих разделов анализа:
 * indicators_analysis, volume_analysis, indicator_correlations,
 * pivot_points, risk_management, feedback
 */
export default function InsightsPanel({ analysis }) {
  // Пример вывода indicators_analysis как таблицы
  const ia = analysis.indicators_analysis || {};
  const va = analysis.volume_analysis || {};
  const ic = analysis.indicator_correlations || {};
  const pp = analysis.pivot_points || {};
  const rm = analysis.risk_management || {};
  const fb = analysis.feedback || {};

  const [show, setShow] = React.useState(false);

  React.useEffect(() => {
    if (analysis && Object.keys(analysis).length) {
      setShow(true);
    }
  }, [analysis]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={show ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }}
    >
      <Box sx={{
        width: '100%',
        maxHeight: '40%',
        bgcolor: '#fafafa',
        overflowY: 'auto',
        p: 1,
        boxSizing: 'border-box',
      }}>
      <Typography variant="h6" sx={{ mt: 1, mb: 1 }}>Indicators Analysis</Typography>
      {Object.entries(ia).map(([key, val]) => (
        typeof val === 'object' && (
          <Box key={key} sx={{ mb: 1 }}>
            <Typography variant="subtitle2">{key}</Typography>
            {Object.entries(val).map(([field, value]) => (
              <Typography key={field} variant="body2">
                {field}: {value}
              </Typography>
            ))}
          </Box>
        )
      ))}
      <Divider sx={{ my: 1 }} />

      <Typography variant="h6" sx={{ mt: 1, mb: 1 }}>Volume Analysis</Typography>
      {va.volume_trends && <Typography variant="body2">{va.volume_trends}</Typography>}
      {(va.significant_volume_changes || []).map((item,i) => (
        <Typography key={i} variant="body2">
          {item.date}: {item.explanation}
        </Typography>
      ))}
      <Divider sx={{ my: 1 }} />

      <Typography variant="h6" sx={{ mt: 1, mb: 1 }}>Indicator Correlations</Typography>
      {ic.explanation && <Typography variant="body2">{ic.explanation}</Typography>}
      <Divider sx={{ my: 1 }} />

      <Typography variant="h6" sx={{ mt: 1, mb: 1 }}>Pivot Points</Typography>
      {['daily','weekly','monthly'].map(ps => (
        <Box key={ps}>
          <Typography variant="subtitle2">{ps.toUpperCase()}</Typography>
          {(pp[ps] || []).map((p,i) => (
            <Typography key={i} variant="body2">
              {p.date}: Pivot={p.pivot}, S1={p.support1}, R1={p.resistance1}
            </Typography>
          ))}
        </Box>
      ))}
      <Divider sx={{ my: 1 }} />

      <Typography variant="h6" sx={{ mt: 1, mb: 1 }}>Risk Management</Typography>
      {(rm.rules || []).map((rule,i) => (
        <Typography key={i} variant="body2">{rule}</Typography>
      ))}
      <Divider sx={{ my: 1 }} />

      <Typography variant="h6" sx={{ mt: 1, mb: 1 }}>Feedback</Typography>
      {fb.note && <Typography variant="body2">{fb.note}</Typography>}
      {fb.suggestions && <Typography variant="body2">{fb.suggestions}</Typography>}
      </Box>
    </motion.div>
  );
}

InsightsPanel.propTypes = {
  analysis: PropTypes.object.isRequired,
};
