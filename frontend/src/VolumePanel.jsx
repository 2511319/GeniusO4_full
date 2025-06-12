import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { createChart } from 'lightweight-charts';

/**
 * VolumePanel рендерит два графика:
 * 1. Гистограмма объёма торгов (volumeData)
 * 2. Линейный график OBV (obvData)
 *
 * Props:
 * - volumeData: Array<{ time: string|number, value: number, color?: string }>
 * - obvData:    Array<{ time: string|number, value: number }>
 */
export default function VolumePanel({ volumeData, obvData }) {
  const containerRef = useRef();
  const obvRef = useRef();
  const volumeRef = useRef();
  const chartRef = useRef();

  useEffect(() => {
    // Создаём один общий chart, но для гистограммы и линии используем разные priceScaleId или создаём два chart
    chartRef.current = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 160,
      layout: { backgroundColor: '#ffffff', textColor: '#000000' },
      grid: { vertLines: { visible: false }, horzLines: { color: '#eee' } },
      rightPriceScale: { scaleMargins: { top: 0.3, bottom: 0 } },
      timeScale: { timeVisible: true, secondsVisible: false },
    });

    // Гистограмма объёма
    volumeRef.current = chartRef.current.addHistogramSeries({
      priceScaleId: '',
      scaleMargins: { top: 0.7, bottom: 0 },
    });
    volumeRef.current.setData(volumeData);

    // OBV линия
    obvRef.current = chartRef.current.addLineSeries({
      priceFormat: { type: 'volume' },
      lineWidth: 1,
      color: '#1976d2',
    });
    obvRef.current.setData(obvData);

    return () => {
      chartRef.current.remove();
    };
  }, []);

  // Обновление данных
  useEffect(() => {
    if (volumeRef.current) volumeRef.current.setData(volumeData);
  }, [volumeData]);

  useEffect(() => {
    if (obvRef.current) obvRef.current.setData(obvData);
  }, [obvData]);

  return <div ref={containerRef} style={{ width: '100%', height: 160 }} />;
}

VolumePanel.propTypes = {
  volumeData: PropTypes.arrayOf(
    PropTypes.shape({
      time: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      value: PropTypes.number.isRequired,
      color: PropTypes.string,
    })
  ).isRequired,
  obvData: PropTypes.arrayOf(
    PropTypes.shape({
      time: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      value: PropTypes.number.isRequired,
    })
  ).isRequired,
};
