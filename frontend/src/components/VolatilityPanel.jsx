// src/components/VolatilityPanel.jsx

import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { createBasicChart } from '../utils/chartUtils';

/** Рендер ATR (Average True Range) */
export default function VolatilityPanel({ atr }) {
  const ref = useRef();

  useEffect(() => {
    const chart = createBasicChart(
      ref.current,
      ref.current.clientWidth,
      100
    );
    const series = chart.addLineSeries({ color: '#9c27b0', lineWidth: 1 });
    series.setData(atr);
    return () => chart.remove();
  }, [atr]);

  return <div ref={ref} style={{ width: '100%', height: 100 }} />;
}

VolatilityPanel.propTypes = {
  atr: PropTypes.array.isRequired,
};
