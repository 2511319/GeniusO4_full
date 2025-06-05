import React, { useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';

export default function TradingViewChart({ data = [], layers = [] }) {
  const ref = useRef(null);
  const chartRef = useRef();

  useEffect(() => {
    console.log('Отрисовка графика. Длина данных:', data.length, 'слои:', layers);
    if (!data.length) return;
    if (chartRef.current) {
      try {
        chartRef.current.remove();
      } catch (err) {
        console.warn('Ошибка удаления старого графика', err);
      }
    }
    const chart = createChart(ref.current, { height: 500 });
    chartRef.current = chart;
    const candleSeries = chart.addCandlestickSeries();
    const candleData = data.map(c => ({
      time: Math.floor(new Date(c['Open Time']).getTime() / 1000),
      open: c.Open,
      high: c.High,
      low: c.Low,
      close: c.Close
    })).sort((a, b) => a.time - b.time);
    console.log('Данные свечей', candleData.slice(0, 3));
    candleSeries.setData(candleData);

    if (layers.includes('ma50') && data[0].MA_50 !== undefined) {
      console.log('Добавление индикатора MA50');
      const ma50 = chart.addLineSeries({ color: 'orange' });
      ma50.setData(
        data
          .map(c => ({
            time: Math.floor(new Date(c['Open Time']).getTime() / 1000),
            value: c.MA_50,
          }))
          .sort((a, b) => a.time - b.time)
      );
    }
    if (layers.includes('ma200') && data[0].MA_200 !== undefined) {
      console.log('Добавление индикатора MA200');
      const ma200 = chart.addLineSeries({ color: 'purple' });
      ma200.setData(
        data
          .map(c => ({
            time: Math.floor(new Date(c['Open Time']).getTime() / 1000),
            value: c.MA_200,
          }))
          .sort((a, b) => a.time - b.time)
      );
    }
    if (layers.includes('volume')) {
      console.log('Добавление гистограммы объёма');
      const vol = chart.addHistogramSeries({ priceFormat: { type: 'volume' }, color: '#26a69a' });
      vol.setData(
        data
          .map(c => ({
            time: Math.floor(new Date(c['Open Time']).getTime() / 1000),
            value: c.Volume,
          }))
          .sort((a, b) => a.time - b.time)
      );
    }

    return () => {
      if (chartRef.current) {
        try {
          chartRef.current.remove();
        } catch (err) {
          console.warn('Ошибка очистки графика', err);
        } finally {
          chartRef.current = null;
        }
      }
    };
  }, [data, layers]);

  return <div ref={ref} className="chart" />;
}
