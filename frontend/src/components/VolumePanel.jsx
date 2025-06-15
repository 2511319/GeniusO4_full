// src/components/VolumePanel.jsx

import React, { useEffect, useRef, useMemo } from 'react';
import PropTypes from 'prop-types';
import { createBasicChart } from '../utils/chartUtils';

/**
 * Рендерит объём и OBV в одном чарте.
 */
export default function VolumePanel({ volumeData, obvData }) {
  const ref = useRef();
  const coloredVolume = useMemo(
    () => volumeData.map(d => ({
      time: d.time,
      value: d.value,
      color: d.open > d.close ? '#e74c3c' : '#2ecc71',
    })),
    [volumeData]
  );

  useEffect(() => {
    const chart = createBasicChart(
      ref.current,
      ref.current.clientWidth,
      160,
      {
        layout: {
          backgroundColor: '#ffffff',
          textColor: '#000000',
        },
        rightPriceScale: { scaleMargins: { top: 0.3, bottom: 0 } },
        timeScale: { timeVisible: true },
      }
    );

    const volSeries = chart.addHistogramSeries({
      priceScaleId: '',
      scaleMargins: { top: 0.7, bottom: 0 },
      color: '#2ecc71',
    });
    volSeries.setData(coloredVolume);

    const obvSeries = chart.addLineSeries({
      color: '#1976d2',
      lineWidth: 1,
    });
    obvSeries.setData(obvData);

    return () => chart.remove();
  }, [coloredVolume, obvData]);

  return <div ref={ref} style={{ width: '100%', height: 160 }} />;
}

VolumePanel.propTypes = {
  volumeData: PropTypes.array.isRequired,
  obvData:    PropTypes.array.isRequired,
};
