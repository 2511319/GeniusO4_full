import React from 'react';
import {
  Box,
  FormControlLabel,
  Checkbox
} from '@mui/material';
import IndicatorGroup from './IndicatorGroup';
import {
  overlays,
  volume,
  momentum,
  volatility,
  macd,
  modelAnalysis,
  forecast
} from './indicatorGroups';

// Группы индикаторов
const GROUPS = [
  { title: 'Overlays', indicators: overlays },
  { title: 'Volume', indicators: volume },
  { title: 'Momentum', indicators: momentum },
  { title: 'Volatility', indicators: volatility },
  { title: 'MACD', indicators: macd },
  { title: 'Model Analysis', indicators: modelAnalysis },
  { title: 'Forecast', indicators: forecast }
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
        control={
          <Checkbox
            checked={showSR}
            onChange={(e) => {
              e.stopPropagation();
              setShowSR(e.target.checked);
            }}
            onClick={(e) => e.stopPropagation()}
          />
        }
        label="Algo-SRlevel"
      />
      <FormControlLabel
        control={
          <Checkbox
            checked={showTrends}
            onChange={(e) => {
              e.stopPropagation();
              setShowTrends(e.target.checked);
            }}
            onClick={(e) => e.stopPropagation()}
          />
        }
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
