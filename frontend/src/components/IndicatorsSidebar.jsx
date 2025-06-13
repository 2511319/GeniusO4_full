// src/components/IndicatorsSidebar.jsx

import React from 'react';
import PropTypes from 'prop-types';
import {
  Drawer,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Checkbox,
  FormControlLabel,
  Typography,
  Box,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

import groups, {
  overlays,
  volume,
  momentum,
  volatility,
  macd,
  modelAnalysis,
  forecast,
} from '../data/indicatorGroups';

export default function IndicatorsSidebar({ activeLayers, setActiveLayers }) {
  const toggle = (key) => {
    setActiveLayers(prev =>
      prev.includes(key)
        ? prev.filter(k => k !== key)
        : [...prev, key]
    );
  };

  const renderGroup = (title, keys) => (
    <Accordion key={title} defaultExpanded>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Typography sx={{ mt: 1, mb: 1 }}>{title}</Typography>
      </AccordionSummary>
      <AccordionDetails>
        {keys.map(key => (
          <FormControlLabel
            key={key}
            control={
              <Checkbox
                checked={activeLayers.includes(key)}
                onChange={() => toggle(key)}
              />
            }
            label={key}
          />
        ))}
      </AccordionDetails>
    </Accordion>
  );

  return (
    <Drawer
      variant="permanent"
      anchor="left"
      sx={{ width: 240, flexShrink: 0, zIndex: 1 }}
    >
      <Box sx={{ width: 240, pt: 2, p: 1, boxSizing: 'border-box' }}>
        {renderGroup('Overlays', overlays)}
        {renderGroup('Volume', volume)}
        {renderGroup('Momentum', momentum)}
        {renderGroup('Volatility', volatility)}
        {renderGroup('MACD', macd)}
        {renderGroup('Model Analysis', modelAnalysis)}
        {renderGroup('Forecast', forecast)}
      </Box>
    </Drawer>
  );
}

IndicatorsSidebar.propTypes = {
  activeLayers:  PropTypes.arrayOf(PropTypes.string).isRequired,
  setActiveLayers: PropTypes.func.isRequired,
};
