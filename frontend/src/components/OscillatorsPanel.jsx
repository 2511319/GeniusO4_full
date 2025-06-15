// src/components/OscillatorsPanel.jsx

import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { Box, useTheme } from '@mui/material';
import { createChart } from 'lightweight-charts';

/** Рендер RSI, Stochastic и Williams %R в отдельных панелях */
export default function OscillatorsPanel({ rsi, stochastic, williams }) {
  const rsiRef     = useRef();
  const stoRef     = useRef();
  const willRef    = useRef();
  const theme      = useTheme();

  useEffect(() => {
    // RSI
    const rsiChart = createChart(rsiRef.current, {
      width:  rsiRef.current.clientWidth,
      height: 120,
      layout: {
        backgroundColor: theme.palette.background.default,
        textColor: theme.palette.text.primary,
      },
      grid: { vertLines: { visible: false }, horzLines: { color: '#eee' } },
    });
    const rsiSeries = rsiChart.addLineSeries({ color: '#ff5722' });
    rsiSeries.setData(rsi);
    rsiChart.applyOptions({ rightPriceScale:{ scaleMargins:{ top:0.2,bottom:0.2 } } });

    // Stochastic
    const stoChart = createChart(stoRef.current, {
      width:  stoRef.current.clientWidth,
      height: 120,
      layout: {
        backgroundColor: theme.palette.background.default,
        textColor: theme.palette.text.primary,
      },
      grid: { vertLines: { visible: false }, horzLines: { color: '#eee' } },
    });
    const kSeries = stoChart.addLineSeries({ color: '#2962ff' });
    const dSeries = stoChart.addLineSeries({ color: '#c62828' });
    kSeries.setData(stochastic.k);
    dSeries.setData(stochastic.d);

    // Williams %R
    const wilChart = createChart(willRef.current, {
      width:  willRef.current.clientWidth,
      height: 120,
      layout: {
        backgroundColor: theme.palette.background.default,
        textColor: theme.palette.text.primary,
      },
      grid: { vertLines: { visible: false }, horzLines: { color: '#eee' } },
    });
    const wilSeries = wilChart.addLineSeries({ color: '#00796b' });
    wilSeries.setData(williams);

    return () => {
      rsiChart.remove();
      stoChart.remove();
      wilChart.remove();
    };
  }, [rsi, stochastic, williams, theme]);

  return (
    <Box>
      <Box ref={rsiRef} sx={{ mb: 1 }} />
      <Box ref={stoRef} sx={{ mb: 1 }} />
      <Box ref={willRef} />
    </Box>
  );
}

OscillatorsPanel.propTypes = {
  rsi:        PropTypes.array.isRequired,
  stochastic: PropTypes.shape({
    k: PropTypes.array.isRequired,
    d: PropTypes.array.isRequired,
  }).isRequired,
  williams:   PropTypes.array.isRequired,
};
