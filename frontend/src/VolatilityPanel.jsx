import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { createChart } from 'lightweight-charts';

/**
 * VolatilityPanel рендерит ATR (Average True Range)
 *
 * Props:
 * - atr: Array<{ time: string|number, value: number }>
 */
export default function VolatilityPanel({ atr }) {
  const containerRef = useRef();

  useEffect(() => {
    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 100,
      layout: { backgroundColor: '#fff', textColor: '#000' },
      grid: { vertLines: { visible: false }, horzLines: { color: '#eee' } },
      rightPriceScale: { scaleMargins: { top: 0.1, bottom: 0.9 } },
      timeScale: { timeVisible: true },
    });
    const series = chart.addLineSeries({ color: '#9c27b0', lineWidth: 1 });
    series.setData(atr);

    return () => {
      chart.remove();
    };
  }, [atr]);

  return <div ref={containerRef} style={{ width: '100%', height: 100 }} />;
}

VolatilityPanel.propTypes = {
  atr: PropTypes.arrayOf(
    PropTypes.shape({
      time: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      value: PropTypes.number.isRequired,
    })
  ).isRequired,
};
