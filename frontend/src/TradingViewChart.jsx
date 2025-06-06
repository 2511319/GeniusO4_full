import React, { useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';
import { indicatorColumnMap } from './indicatorGroups';

export default function TradingViewChart({ data = [], layers = [] }) {
  const mainRef = useRef(null);
  const panelRef = useRef(null);
  const chartRef = useRef({});

  const panelIndicators = new Set([
    'RSI',
    'MACD',
    'OBV',
    'ATR',
    'ADX',
    'Stochastic_Oscillator',
    "Williams_%R",
    'Volume'
  ]);

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
    Volume: '#26a69a'
  };

  useEffect(() => {
    console.log('Отрисовка графика. Длина данных:', data.length, 'слои:', layers);
    if (!data.length) return;
    // очистка старых графиков
    Object.values(chartRef.current).forEach((ch) => {
      try {
        ch.remove();
      } catch (err) {
        console.warn('Ошибка удаления графика', err);
      }
    });
    chartRef.current = {};

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

    const addLine = (chart, field, color) => {
      const series = chart.addLineSeries({ color });
      series.setData(buildSeriesData(field));
    };

    const addHistogram = (chart, field, color) => {
      const series = chart.addHistogramSeries({ color, priceFormat: { type: 'volume' } });
      series.setData(buildSeriesData(field));
    };

    const mainChart = createChart(mainRef.current, { height: 500 });
    chartRef.current.main = mainChart;
    const candleSeries = mainChart.addCandlestickSeries();
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


    const overlayLayers = layers.filter((l) => !panelIndicators.has(l));
    const panelLayers = layers.filter((l) => panelIndicators.has(l));

    overlayLayers.forEach((layer) => {
      const cols = indicatorColumnMap[layer] || [layer];
      if (!cols.some((c) => data[0][c] !== undefined)) return;
      if (layer === 'Bollinger_Bands') {
        addLine(mainChart, 'Bollinger_Middle', colors.Bollinger_Middle);
        addLine(mainChart, 'Bollinger_Upper', colors.Bollinger_Upper);
        addLine(mainChart, 'Bollinger_Lower', colors.Bollinger_Lower);
      } else if (layer === 'Ichimoku_Cloud') {
        addLine(mainChart, 'Ichimoku_A', colors.Ichimoku_A);
        addLine(mainChart, 'Ichimoku_B', colors.Ichimoku_B);
        addLine(mainChart, 'Ichimoku_Base_Line', colors.Ichimoku_Base_Line);
        addLine(mainChart, 'Ichimoku_Conversion_Line', colors.Ichimoku_Conversion_Line);
      } else if (layer === 'Moving_Average_Envelopes') {
        addLine(mainChart, 'Moving_Average_Envelope_Upper', colors.Moving_Average_Envelope_Upper);
        addLine(mainChart, 'Moving_Average_Envelope_Lower', colors.Moving_Average_Envelope_Lower);
      } else {
        addLine(mainChart, layer, colors[layer] || 'black');
      }
    });

    let panelChart = null;
    if (panelLayers.length) {
      panelChart = createChart(panelRef.current, { height: 200 });
      chartRef.current.panel = panelChart;
    }

    const times = data
      .map((c) => toUnix(c['Open Time']))
      .filter((t) => t !== null);
    const buildConstData = (val) => times.map((time) => ({ time, value: val }));

    panelLayers.forEach((layer) => {
      if (!panelChart) return;
      if (layer === 'Volume') {
        addHistogram(panelChart, 'Volume', colors.Volume);
      } else if (layer === 'MACD') {
        addLine(panelChart, 'MACD', colors.MACD);
        addLine(panelChart, 'MACD_signal', colors.MACD_signal);
        addHistogram(panelChart, 'MACD_hist', colors.MACD_hist);
      } else if (layer === 'RSI') {
        addLine(panelChart, 'RSI', colors.RSI);
        const over = panelChart.addLineSeries({ color: 'rgba(255,0,0,0.5)', lineStyle: 2 });
        over.setData(buildConstData(70));
        const under = panelChart.addLineSeries({ color: 'rgba(0,128,0,0.5)', lineStyle: 2 });
        under.setData(buildConstData(30));
      } else {
        addLine(panelChart, layer, colors[layer] || 'black');
      }
    });

    return () => {
      Object.values(chartRef.current).forEach((ch) => {
        try {
          ch.remove();
        } catch (err) {
          console.warn('Ошибка очистки графика', err);
        }
      });
      chartRef.current = {};
    };
  }, [data, layers]);

  const panelLayers = layers.filter((l) => panelIndicators.has(l));

  return (
    <div className="chart-panels">
      <div className="legend">
        <span className="legend-item"><span className="legend-color" style={{background:'gray'}}></span>Свечи</span>
        {layers.map((l) => (
          <span key={l} className="legend-item"><span className="legend-color" style={{background:colors[l]||'black'}}></span>{l}</span>
        ))}
      </div>
      <div ref={mainRef} className="chart" />
      {panelLayers.length > 0 && (
        <div ref={panelRef} className="chart-panel" />
      )}
    </div>
  );
}
