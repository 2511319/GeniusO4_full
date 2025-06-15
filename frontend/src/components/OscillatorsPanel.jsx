// src/components/OscillatorsPanel.jsx

import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
// Используем простые элементы вместо MUI

import { createBasicChart } from '../utils/chartUtils';

/** Рендер RSI, Stochastic и Williams %R в отдельных панелях */
export default function OscillatorsPanel({ rsi, stochastic, williams }) {
  const rsiRef     = useRef();
  const stoRef     = useRef();
  const willRef    = useRef();

  useEffect(() => {
    // RSI
    const rsiChart = createBasicChart(
      rsiRef.current,
      rsiRef.current.clientWidth,
      120,
      {
        layout: {
          backgroundColor: '#ffffff',
          textColor: '#000000',
        },
      }
    );
    const rsiSeries = rsiChart.addLineSeries({ color: '#ff5722' });
    rsiSeries.setData(rsi);
    rsiChart.applyOptions({ rightPriceScale:{ scaleMargins:{ top:0.2,bottom:0.2 } } });

    // Stochastic
    const stoChart = createBasicChart(
      stoRef.current,
      stoRef.current.clientWidth,
      120,
      {
        layout: {
          backgroundColor: '#ffffff',
          textColor: '#000000',
        },
      }
    );
    const kSeries = stoChart.addLineSeries({ color: '#2962ff' });
    const dSeries = stoChart.addLineSeries({ color: '#c62828' });
    kSeries.setData(stochastic.k);
    dSeries.setData(stochastic.d);

    // Williams %R
    const wilChart = createBasicChart(
      willRef.current,
      willRef.current.clientWidth,
      120,
      {
        layout: {
          backgroundColor: '#ffffff',
          textColor: '#000000',
        },
      }
    );
    const wilSeries = wilChart.addLineSeries({ color: '#00796b' });
    wilSeries.setData(williams);

    return () => {
      rsiChart.remove();
      stoChart.remove();
      wilChart.remove();
    };
  }, [rsi, stochastic, williams]);

  return (
    <div>
      <div ref={rsiRef} className="mb-1" />
      <div ref={stoRef} className="mb-1" />
      <div ref={willRef} />
    </div>
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
