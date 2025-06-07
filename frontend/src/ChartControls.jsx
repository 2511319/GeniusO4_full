import React from 'react';
import { ToggleButtonGroup, ToggleButton, Box } from '@mui/material';

export default function ChartControls({ type, onChange }) {
  return (
    <Box sx={{ px: 1, py: 0.5 }}>
      <ToggleButtonGroup
        exclusive size="small" color="primary"
        value={type} onChange={(_, val) => val && onChange(val)}
      >
        <ToggleButton value="candles">Candle</ToggleButton>
        <ToggleButton value="heikin">Heikin-Ashi</ToggleButton>
        <ToggleButton value="renko">Renko</ToggleButton>
      </ToggleButtonGroup>
    </Box>
  );
}
