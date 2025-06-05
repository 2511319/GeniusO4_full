import React, { useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';

export default function TradingViewChart({ data = [], layers = [] }) {
  const ref = useRef(null);
  const chartRef = useRef();

  useEffect(() => {
    console.log('Отрисовка графика. Длина данных:', data.length, 'слои:', layers);
    if (!data.length) return;
    if (chartRef.current) {
      chartRef.current.remove();
    }
    const chart = createChart(ref.current, { height: 500 });
    chartRef.current = chart;
    const candleSeries = chart.addCandlestickSeries();
    candleSeries.setData(
      data.map(c => ({
        time: c['Open Time'].slice(0, 10),
        open: c.Open,
        high: c.High,
        low: c.Low,
        close: c.Close
      }))
    );

    if (layers.includes('ma50') && data[0].MA_50 !== undefined) {
      const ma50 = chart.addLineSeries({ color: 'orange' });
      ma50.setData(data.map(c => ({ time: c['Open Time'].slice(0, 10), value: c.MA_50 })));
    }
    if (layers.includes('ma200') && data[0].MA_200 !== undefined) {
      const ma200 = chart.addLineSeries({ color: 'purple' });
      ma200.setData(data.map(c => ({ time: c['Open Time'].slice(0, 10), value: c.MA_200 })));
    }
    if (layers.includes('volume')) {
      const vol = chart.addHistogramSeries({ priceFormat: { type: 'volume' }, color: '#26a69a' });
      vol.setData(data.map(c => ({ time: c['Open Time'].slice(0, 10), value: c.Volume })));
    }

    return () => chart.remove();
  }, [data, layers]);

  return <div ref={ref} className="chart" />;
}
