import React from 'react';
import {
  Box,
  Typography,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Divider
} from '@mui/material';
import IndicatorGroup from './IndicatorGroup';
import {
  advancedIndicators,
  modelAnalysisIndicators
} from './indicatorGroups';

// Группы индикаторов 1–7
const GROUPS = [
  {
    title: 'Группа 1',
    indicators: ['Volume', 'RSI', 'MACD', 'OBV', 'ATR', 'VWAP'],
  },
  {
    title: 'Группа 2',
    indicators: ['MA_20', 'MA_50', 'MA_100', 'MA_200', 'ADX', 'Parabolic_SAR', 'Ichimoku_Cloud'],
  },
  {
    title: 'Группа 3',
    indicators: ['Stochastic_Oscillator', 'Williams_%R', 'Bollinger_Bands', 'Moving_Average_Envelopes'],
  },
  {
    title: 'Группа 4',
    indicators: ['support_resistance_levels', 'trend_lines', 'unfinished_zones', 'imbalances', 'structural_edge'],
  },
  {
    title: 'Группа 5',
    indicators: ['fibonacci_analysis', 'elliott_wave_analysis'],
  },
  {
    title: 'Группа 6',
    indicators: ['candlestick_patterns', 'divergence_analysis', 'fair_value_gaps', 'gap_analysis', 'psychological_levels', 'anomalous_candles'],
  },
  {
    title: 'Группа 7',
    indicators: [...modelAnalysisIndicators],
  }
];

export default function IndicatorsSidebar({
  layers,
  toggleLayer,
  showSR,
  setShowSR,
  showTrends,
  setShowTrends,
}) {
  return (
    <Box>
      {/* базовые индикаторы и опции */}
      <Typography variant="subtitle1">{GROUPS[0].title}</Typography>
      <FormGroup>
        {GROUPS[0].indicators.map((ind) => (
          <FormControlLabel
            key={ind}
            control={<Checkbox checked={layers.includes(ind)} onChange={() => toggleLayer(ind)} />}
            label={ind}
          />
        ))}
        <FormControlLabel
          control={<Checkbox checked={showSR} onChange={(e) => setShowSR(e.target.checked)} />}
          label="Algo-SRlevel"
        />
        <FormControlLabel
          control={<Checkbox checked={showTrends} onChange={(e) => setShowTrends(e.target.checked)} />}
          label="Trend lines"
        />
      </FormGroup>
      <Divider sx={{ my: 1 }} />
      {/* остальные группы */}
      {GROUPS.slice(1).map(({ title, indicators }) => (
        <IndicatorGroup
          key={title}
          title={title}
          indicators={indicators}
          layers={layers}
          toggleLayer={toggleLayer}
        />
      ))}
    </Box>
  );
}
