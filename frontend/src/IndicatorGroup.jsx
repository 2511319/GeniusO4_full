import React from 'react';
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControlLabel,
  Checkbox,
  Typography
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

export default function IndicatorGroup({ title, indicators, layers, toggleLayer, extraControls }) {
  if (!indicators.length && !extraControls) return null;
  return (
    <Accordion disableGutters>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Typography variant="subtitle1">{title}</Typography>
      </AccordionSummary>
      <AccordionDetails>
        {indicators.map((ind) => (
          <FormControlLabel
            key={ind}
            control={
              <Checkbox
                checked={layers.includes(ind)}
                onChange={(e) => {
                  e.stopPropagation();
                  toggleLayer(ind);
                }}
                onClick={(e) => e.stopPropagation()}
              />
            }
            label={ind}
          />
        ))}
        {extraControls}
      </AccordionDetails>
    </Accordion>
  );
}
