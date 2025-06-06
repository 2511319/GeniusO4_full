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
    const seen = new Set();
    const candleData = data
      .map((c) => {
        const time = Math.floor(new Date(c['Open Time']).getTime() / 1000);
        if (!time || Number.isNaN(time)) return null;
        return { time, open: c.Open, high: c.High, low: c.Low, close: c.Close };
      })
      .filter((c) => c && !seen.has(c.time) && seen.add(c.time))
      .sort((a, b) => a.time - b.time);
    console.log('Данные свечей', candleData.slice(0, 3));
    try {
      candleSeries.setData(candleData);
    } catch (err) {
      console.error('Ошибка setData', err);
    }

    if (layers.includes('MA_50') && data[0].MA_50 !== undefined) {
      console.log('Добавление индикатора MA50');
      const ma50 = chart.addLineSeries({ color: 'orange' });
      ma50.setData(data.map(c => ({ time: c['Open Time'].slice(0, 10), value: c.MA_50 })));
      const seen50 = new Set();
      const seriesData = data
        .map((c) => {
          const t = Math.floor(new Date(c['Open Time']).getTime() / 1000);
          if (!t || Number.isNaN(t)) return null;
          return { time: t, value: c.MA_50 };
        })
        .filter((c) => c && !seen50.has(c.time) && seen50.add(c.time))
        .sort((a, b) => a.time - b.time);
      ma50.setData(seriesData);
    }
    if (layers.includes('MA_200') && data[0].MA_200 !== undefined) {
      console.log('Добавление индикатора MA200');
      const ma200 = chart.addLineSeries({ color: 'purple' });
      const seen200 = new Set();
      const seriesData = data
        .map((c) => {
          const t = Math.floor(new Date(c['Open Time']).getTime() / 1000);
          if (!t || Number.isNaN(t)) return null;
          return { time: t, value: c.MA_200 };
        })
        .filter((c) => c && !seen200.has(c.time) && seen200.add(c.time))
        .sort((a, b) => a.time - b.time);
      ma200.setData(seriesData);
    }
    if (layers.includes('Volume')) {
      console.log('Добавление гистограммы объёма');
      const vol = chart.addHistogramSeries({ priceFormat: { type: 'volume' }, color: '#26a69a' });
      const seenVol = new Set();
      const volData = data
        .map((c) => {
          const t = Math.floor(new Date(c['Open Time']).getTime() / 1000);
          if (!t || Number.isNaN(t)) return null;
          return { time: t, value: c.Volume };
        })
        .filter((c) => c && !seenVol.has(c.time) && seenVol.add(c.time))
        .sort((a, b) => a.time - b.time);
      vol.setData(volData);
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