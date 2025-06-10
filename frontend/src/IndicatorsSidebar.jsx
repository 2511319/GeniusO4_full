import React from 'react';
import {
  Box,
  FormControlLabel,
  Checkbox
} from '@mui/material';
import IndicatorGroup from './IndicatorGroup';
import {
  advancedIndicators,
  modelAnalysisIndicators
} from './indicatorGroups';

// Группы индикаторов
const GROUPS = [
  {
    title: 'Overlays',
    indicators: ['MA_20', 'MA_50', 'MA_100', 'MA_200', 'ADX', 'Parabolic_SAR', 'Ichimoku_Cloud']
  },
  { title: 'Volume', indicators: ['Volume', 'OBV'] },
  { title: 'Momentum', indicators: ['RSI', 'Stochastic_Oscillator', 'Williams_%R'] },
  { title: 'Volatility', indicators: ['ATR'] },
  { title: 'MACD', indicators: ['MACD'] },
  { title: 'Model Analysis', indicators: [...advancedIndicators] },
  { title: 'Forecast', indicators: [...modelAnalysisIndicators] }
];

export default function IndicatorsSidebar({
  layers,
  toggleLayer,
  showSR,
  setShowSR,
  showTrends,
  setShowTrends,
}) {
  const baseExtra = (
    <>
      <FormControlLabel
        control={<Checkbox checked={showSR} onChange={(e) => setShowSR(e.target.checked)} />}
        label="Algo-SRlevel"
      />
      <FormControlLabel
        control={<Checkbox checked={showTrends} onChange={(e) => setShowTrends(e.target.checked)} />}
        label="Trend lines"
      />
    </>
  );
  return (
    <Box>
      {GROUPS.map(({ title, indicators }, idx) => (
        <IndicatorGroup
          key={title}
          title={title}
          indicators={indicators}
          layers={layers}
          toggleLayer={toggleLayer}
          extraControls={idx === 0 ? baseExtra : null}
        />
      ))}
    </Box>
  );
}
