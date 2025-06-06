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

    const toUnix = (d) => {
      const t = Math.floor(new Date(d).getTime() / 1000);
      return !t || Number.isNaN(t) ? null : t;
    };

    const buildSeriesData = (field) => {
      const seen = new Set();
      return data
        .map((c) => {
          const t = toUnix(c['Open Time']);
          if (t === null || c[field] === undefined) return null;
          return { time: t, value: c[field] };
        })
        .filter((c) => c && !seen.has(c.time) && seen.add(c.time))
        .sort((a, b) => a.time - b.time);
    };

    const addLine = (field, color) => {
      const series = chart.addLineSeries({ color });
      series.setData(buildSeriesData(field));
    };

    const addHistogram = (field, color) => {
      const series = chart.addHistogramSeries({ color, priceFormat: { type: 'volume' } });
      series.setData(buildSeriesData(field));
    };

    const chart = createChart(ref.current, { height: 500 });
    chartRef.current = chart;
    const candleSeries = chart.addCandlestickSeries();
    const seenCandles = new Set();
    const candleData = data
      .map((c) => {
        const time = toUnix(c['Open Time']);
        if (time === null) return null;
        return { time, open: c.Open, high: c.High, low: c.Low, close: c.Close };
      })
      .filter((c) => c && !seenCandles.has(c.time) && seenCandles.add(c.time))
      .sort((a, b) => a.time - b.time);
    candleSeries.setData(candleData);

    const colors = {
      MA_20: 'blue',
      MA_50: 'orange',
      MA_100: 'teal',
      MA_200: 'purple',
      RSI: '#ff9800',
      MACD: '#03a9f4',
      MACD_signal: '#e91e63',
      MACD_hist: '#9e9e9e',
      OBV: '#009688',
      ATR: '#795548',
      Stochastic_Oscillator: '#4caf50',
      Bollinger_Middle: '#795548',
      Bollinger_Upper: '#2196f3',
      Bollinger_Lower: '#f44336',
      ADX: '#9c27b0',
      "Williams_%R": '#673ab7',
      Parabolic_SAR: '#3f51b5',
      Ichimoku_A: '#00bcd4',
      Ichimoku_B: '#009688',
      Ichimoku_Base_Line: '#ff5722',
      Ichimoku_Conversion_Line: '#e91e63',
      VWAP: '#607d8b',
      Moving_Average_Envelope_Upper: '#8bc34a',
      Moving_Average_Envelope_Lower: '#8bc34a',
      Volume: '#26a69a',
    };

    layers.forEach((layer) => {
      if (data[0][layer] === undefined && layer !== 'Volume') return;
      if (layer === 'Volume') {
        addHistogram('Volume', colors.Volume);
      } else if (layer === 'MACD_hist') {
        addHistogram('MACD_hist', colors.MACD_hist);
      } else {
        addLine(layer, colors[layer] || 'black');
      }
    });

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
