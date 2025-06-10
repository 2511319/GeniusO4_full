import React, { useEffect, useRef } from 'react';
import { Box } from '@mui/material';
import { createChart } from 'lightweight-charts';

const OSC_FIELDS = ['RSI', 'Stochastic_Oscillator', 'Williams_%R', 'OBV'];

export default function OscillatorsPanel({ data = [], layers = [] }) {
  const ref = useRef();
  useEffect(() => {
    if (!ref.current) return;
    ref.current.innerHTML = '';
    const chart = createChart(ref.current, {
      height: 120,
      layout: { background: { color: '#121212' }, textColor: '#c7c7c7' },
      grid: { vertLines: { color: '#2a2a2a' }, horzLines: { color: '#2a2a2a' } },
      width: ref.current.clientWidth,
      localization: { locale: 'ru-RU' },
    });
    const colors = ['#ff9800', '#2196f3', '#9c27b0', '#009688'];
    OSC_FIELDS.forEach((name, idx) => {
      if (!layers.includes(name) || !data[0] || data[0][name] === undefined) return;
      const series = chart.addLineSeries({ color: colors[idx % colors.length] });
      series.applyOptions({ priceFormat: { type: 'none' } });
      series.setData(data.map((d) => ({ time: d.time, value: d[name] })));
    });
    chart.timeScale().fitContent();
    const resize = () => chart.resize(ref.current.clientWidth, 120);
    window.addEventListener('resize', resize);
    return () => {
      window.removeEventListener('resize', resize);
    };
  }, [data, layers]);
  return <Box ref={ref} sx={{ height: 120 }} className="chart-panel" />;
}
