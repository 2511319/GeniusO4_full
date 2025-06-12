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
        <Typography>{title}</Typography>
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
      sx={{ width: 240, flexShrink: 0 }}
    >
      <div style={{ width: 240, paddingTop: 16 }}>
        {renderGroup('Overlays', overlays)}
        {renderGroup('Volume', volume)}
        {renderGroup('Momentum', momentum)}
        {renderGroup('Volatility', volatility)}
        {renderGroup('MACD', macd)}
        {renderGroup('Model Analysis', modelAnalysis)}
        {renderGroup('Forecast', forecast)}
      </div>
    </Drawer>
  );
}

IndicatorsSidebar.propTypes = {
  activeLayers:  PropTypes.arrayOf(PropTypes.string).isRequired,
  setActiveLayers: PropTypes.func.isRequired,
};
