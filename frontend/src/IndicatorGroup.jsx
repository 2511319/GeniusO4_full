import React from 'react';
import { Box, FormControlLabel, Checkbox, Typography } from '@mui/material';

export default function IndicatorGroup({ title, indicators, layers, toggleLayer }) {
  if (!indicators.length) return null;
  return (
    <Box sx={{ mb: 1 }}>
      <Typography variant="subtitle1">{title}</Typography>
      {indicators.map((ind) => (
        <FormControlLabel
          key={ind}
          control={<Checkbox checked={layers.includes(ind)} onChange={() => toggleLayer(ind)} />}
          label={ind}
        />
      ))}
    </Box>
  );
}
