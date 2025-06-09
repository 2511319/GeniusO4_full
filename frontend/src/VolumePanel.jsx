import React, { useEffect, useRef } from 'react';
import { Box } from '@mui/material';
import { createChart } from 'lightweight-charts';

export default function VolumePanel({ data = [] }) {
  const ref = useRef();
  useEffect(() => {
    if (!ref.current) return;
    ref.current.innerHTML = '';
    const chart = createChart(ref.current, {
      height: 100,
      layout: { background: { color: '#121212' }, textColor: '#c7c7c7' },
      grid: { vertLines: { color: '#2a2a2a' }, horzLines: { color: '#2a2a2a' } },
      width: ref.current.clientWidth,
      localization: { locale: 'ru-RU' },
    });
    const series = chart.addHistogramSeries({ color: '#4caf50' });
    series.setData(data.map((d) => ({ time: d.time, value: d.Volume })));
    chart.timeScale().fitContent();
    const resize = () => chart.resize(ref.current.clientWidth, 100);
    window.addEventListener('resize', resize);
    return () => {
      window.removeEventListener('resize', resize);
    };
  }, [data]);
  return <Box ref={ref} sx={{ height: 100 }} className="chart-panel" />;
}
