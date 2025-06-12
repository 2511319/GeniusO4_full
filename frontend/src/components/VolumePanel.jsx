// src/components/VolumePanel.jsx

import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { createChart } from 'lightweight-charts';

/**
 * Рендерит объём и OBV в одном чарте.
 */
export default function VolumePanel({ volumeData, obvData }) {
  const ref = useRef();

  useEffect(() => {
    const chart = createChart(ref.current, {
      width: ref.current.clientWidth,
      height: 160,
      layout: { backgroundColor: '#fff', textColor: '#000' },
      grid: { vertLines: { visible: false }, horzLines: { color: '#eee' } },
      rightPriceScale: { scaleMargins: { top: 0.3, bottom: 0 } },
      timeScale: { timeVisible: true },
    });

    const volSeries = chart.addHistogramSeries({
      priceScaleId: '',
      scaleMargins: { top: 0.7, bottom: 0 },
      color: bar => (bar.open > bar.close ? '#e74c3c' : '#2ecc71'),
    });
    volSeries.setData(volumeData);

    const obvSeries = chart.addLineSeries({
      color: '#1976d2',
      lineWidth: 1,
    });
    obvSeries.setData(obvData);

    return () => chart.remove();
  }, [volumeData, obvData]);

  return <div ref={ref} style={{ width: '100%', height: 160 }} />;
}

VolumePanel.propTypes = {
  volumeData: PropTypes.array.isRequired,
  obvData:    PropTypes.array.isRequired,
};
