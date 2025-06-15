// src/components/MACDPanel.jsx

import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { createBasicChart } from '../utils/chartUtils';
import { useTheme } from '@mui/material';

/** Рендер MACD, Signal и Histogram */
export default function MACDPanel({ macd, signal, histogram }) {
  const ref = useRef();
  const theme = useTheme();

  useEffect(() => {
    const chart = createBasicChart(
      ref.current,
      ref.current.clientWidth,
      120,
      {
        layout: {
          backgroundColor: theme.palette.background.default,
          textColor: theme.palette.text.primary,
        },
      }
    );

    const macdSeries   = chart.addLineSeries({ color: '#007aff', lineWidth: 2 });
    const signalSeries = chart.addLineSeries({ color: '#ff3b30', lineWidth: 1 });
    const histSeries   = chart.addHistogramSeries({
      priceFormat: { type: 'volume' },
      priceScaleId: '',
      color: (bar) => (bar.value >= 0 ? 'rgba(0,200,0,0.5)' : 'rgba(200,0,0,0.5)'),
      scaleMargins: { top: 0.7, bottom: 0 },
    });

    macdSeries.setData(macd);
    signalSeries.setData(signal);
    histSeries.setData(histogram);

    return () => chart.remove();
  }, [macd, signal, histogram, theme]);

  return <div ref={ref} style={{ width: '100%', height: 120 }} />;
}

MACDPanel.propTypes = {
  macd:      PropTypes.array.isRequired,
  signal:    PropTypes.array.isRequired,
  histogram: PropTypes.array.isRequired,
};
