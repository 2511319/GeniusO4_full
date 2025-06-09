import React, { useEffect, useRef } from 'react';
import { Box } from '@mui/material';
import { createChart } from 'lightweight-charts';

export default function MACDPanel({ data = [] }) {
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
    if (data[0] && data[0].MACD !== undefined) {
      const macd = chart.addLineSeries({ color: '#2196f3' });
      macd.setData(data.map((d) => ({ time: d.time, value: d.MACD })));
    }
    if (data[0] && data[0].MACD_signal !== undefined) {
      const signal = chart.addLineSeries({ color: '#ff9800' });
      signal.setData(data.map((d) => ({ time: d.time, value: d.MACD_signal })));
    }
    if (data[0] && data[0].MACD_hist !== undefined) {
      const hist = chart.addHistogramSeries({ color: '#9c27b0' });
      hist.setData(data.map((d) => ({ time: d.time, value: d.MACD_hist })));
    }
    chart.timeScale().fitContent();
    const resize = () => chart.resize(ref.current.clientWidth, 120);
    window.addEventListener('resize', resize);
    return () => {
      window.removeEventListener('resize', resize);
    };
  }, [data]);
  return <Box ref={ref} sx={{ height: 120 }} className="chart-panel" />;
}
