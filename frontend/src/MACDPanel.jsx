import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { createChart } from 'lightweight-charts';

/**
 * MACDPanel рендерит:
 * - MACD Line
 * - Signal Line
 * - Histogram
 *
 * Props:
 * - macd:        Array<{ time: string|number, value: number }>
 * - signal:      Array<{ time: string|number, value: number }>
 * - histogram:   Array<{ time: string|number, value: number }>
 */
export default function MACDPanel({ macd, signal, histogram }) {
  const containerRef = useRef();

  useEffect(() => {
    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 120,
      layout: { backgroundColor: '#fff', textColor: '#000' },
      grid: { vertLines: { visible: false }, horzLines: { color: '#eee' } },
      rightPriceScale: { scaleMargins: { top: 0.3, bottom: 0 } },
      timeScale: { timeVisible: true },
    });

    // MACD Line
    const macdSeries = chart.addLineSeries({ color: '#007aff', lineWidth: 2 });
    macdSeries.setData(macd);

    // Signal Line
    const signalSeries = chart.addLineSeries({ color: '#ff3b30', lineWidth: 1 });
    signalSeries.setData(signal);

    // Histogram
    const histSeries = chart.addHistogramSeries({
      priceFormat: { type: 'volume' },
      priceScaleId: '',
      scaleMargins: { top: 0.7, bottom: 0 },
      color: (hist) => (hist.value >= 0 ? 'rgba(0,200,0,0.5)' : 'rgba(200,0,0,0.5)'),
    });
    histSeries.setData(histogram);

    return () => {
      chart.remove();
    };
  }, [macd, signal, histogram]);

  return <div ref={containerRef} style={{ width: '100%', height: 120 }} />;
}

MACDPanel.propTypes = {
  macd: PropTypes.array.isRequired,
  signal: PropTypes.array.isRequired,
  histogram: PropTypes.array.isRequired,
};
