import React, { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';
import { indicatorColumnMap } from './indicatorGroups';

export default function TradingViewChart({ data = [], layers = [], analysis = {} }) {
  const mainRef = useRef(null);
  const panelRef = useRef(null);
  const containerRef = useRef(null);
  const chartRef = useRef({});
  const [panelRatio, setPanelRatio] = useState(0.3);

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
    Volume: '#26a69a',
    trend_lines: '#2196f3',
    fibonacci_analysis: 'purple',
    elliott_wave_analysis: '#00ff00',
    structural_edge: '#00ffff',
    candlestick_patterns: '#ff00ff',
    divergence_analysis: '#ff0000',
    fair_value_gaps: '#00ffff',
    recommendations: '#ffa500'
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
      if (!d) return null;
      const parsed = new Date(
        typeof d === 'string' ? d.replace(' ', 'T') + 'Z' : d
      );
      const t = Math.floor(parsed.getTime() / 1000);
      if (!t || Number.isNaN(t)) {
        console.warn('Не удалось распознать дату', d);
        return null;
      }
      return t;
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
      return series;
    };

    const addHistogram = (chart, field, color) => {
      const series = chart.addHistogramSeries({ color, priceFormat: { type: 'volume' } });
      series.setData(buildSeriesData(field));
      return series;
    };

    const mainChart = createChart(mainRef.current, {
      height: 500,
      layout: {
        background: { color: '#121212' },
        textColor:  '#c7c7c7',
      },
      grid: {
        vertLines: { color: '#2a2a2a' },
        horzLines: { color: '#2a2a2a' },
      },
    });
    chartRef.current.main = mainChart;
    mainChart.applyOptions({ rightPriceScale: { visible: true }, leftPriceScale: { visible: true } });
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

    chartRef.current.overlays = [];

    if (layers.includes('support_resistance_levels')) {
      const levels = analysis.support_resistance_levels || {};
      const lastTime = candleData[candleData.length - 1]?.time;
      const addSR = (items, color) => {
        items?.forEach((l) => {
          const series = mainChart.addLineSeries({ color, lineStyle: 2 });
          series.setData([
            { time: toUnix(l.date), value: l.level },
            { time: lastTime, value: l.level },
          ]);
          chartRef.current.overlays.push(series);
        });
      };
      addSR(levels.supports, 'green');
      addSR(levels.resistances, 'red');
    }

    if (layers.includes('price_prediction')) {
      const candles = analysis.price_prediction?.virtual_candles || [];
      if (candles.length) {
        const series = mainChart.addCandlestickSeries({
          upColor: 'purple',
          downColor: 'purple',
          borderVisible: false,
        });
        const predData = candles
          .map((c) => ({
            time: toUnix(c.date),
            open: c.open,
            high: c.high,
            low: c.low,
            close: c.close,
          }))
          .filter((c) => c.time)
          .sort((a, b) => a.time - b.time);
        series.setData(predData);
        chartRef.current.overlays.push(series);
      }
    }

    const markers = [];

    if (layers.includes('psychological_levels')) {
      const levels = analysis.psychological_levels?.levels || [];
      const lastTime = candleData[candleData.length - 1]?.time;
      levels.forEach((l) => {
        const color = l.type === 'Support' ? 'blue' : 'orange';
        const series = mainChart.addLineSeries({ color, lineStyle: 2 });
        series.setData([
          { time: toUnix(l.date), value: l.level },
          { time: lastTime, value: l.level },
        ]);
        chartRef.current.overlays.push(series);
      });
    }

    if (layers.includes('unfinished_zones')) {
      const zones = analysis.unfinished_zones || [];
      zones.forEach((z) => {
        markers.push({
          time: toUnix(z.date),
          position: 'aboveBar',
          color: z.line_color || 'purple',
          shape: 'circle',
          text: z.type,
        });
      });
    }

    if (layers.includes('gap_analysis')) {
      const gaps = analysis.gap_analysis?.gaps || [];
      gaps.forEach((g) => {
        markers.push({
          time: toUnix(g.date),
          position: 'aboveBar',
          color: 'red',
          shape: 'arrowDown',
          text: g.gap_type,
        });
      });
    }

    if (layers.includes('imbalances')) {
      const imbs = analysis.imbalances || [];
      imbs.forEach((im) => {
        const from = toUnix(im.start_point?.date);
        const to = toUnix(im.end_point?.date);
        if (from && to) {
          const series = mainChart.addAreaSeries({
            lineColor: 'rgba(255,0,0,0.3)',
            topColor: 'rgba(255,0,0,0.1)',
            bottomColor: 'rgba(255,0,0,0.1)',
          });
          series.setData([
            { time: from, value: im.price_range?.[0] || im.start_point.price },
            { time: to, value: im.price_range?.[0] || im.start_point.price },
          ]);
          const series2 = mainChart.addAreaSeries({
            lineColor: 'rgba(255,0,0,0.3)',
            topColor: 'rgba(255,0,0,0.1)',
            bottomColor: 'rgba(255,0,0,0.1)',
          });
          series2.setData([
            { time: from, value: im.price_range?.[1] || im.end_point.price },
            { time: to, value: im.price_range?.[1] || im.end_point.price },
          ]);
          chartRef.current.overlays.push(series, series2);
        }
      });
    }

    if (layers.includes('trend_lines')) {
      const lines = analysis.trend_lines?.lines || [];
      lines.forEach((ln) => {
        const series = mainChart.addLineSeries({ color: colors.trend_lines, lineStyle: 2 });
        series.setData([
          { time: toUnix(ln.start_point?.date), value: ln.start_point?.price },
          { time: toUnix(ln.end_point?.date), value: ln.end_point?.price },
        ]);
        chartRef.current.overlays.push(series);
      });
    }

    if (layers.includes('fibonacci_analysis')) {
      const fib = analysis.fibonacci_analysis || {};
      const drawFib = (obj, color) => {
        if (!obj) return;
        const { levels = {}, start_point = {}, end_point = {} } = obj;
        Object.values(levels).forEach((price) => {
          const series = mainChart.addLineSeries({ color, lineStyle: 2 });
          series.setData([
            { time: toUnix(start_point.date), value: price },
            { time: toUnix(end_point.date), value: price },
          ]);
          chartRef.current.overlays.push(series);
        });
      };
      drawFib(fib.based_on_global_trend, 'purple');
      drawFib(fib.based_on_local_trend, 'green');
    }

    if (layers.includes('elliott_wave_analysis')) {
      const waves = analysis.elliott_wave_analysis?.waves || [];
      waves.forEach((w) => {
        const series = mainChart.addLineSeries({ color: colors.elliott_wave_analysis });
        series.setData([
          { time: toUnix(w.start_point?.date), value: w.start_point?.price },
          { time: toUnix(w.end_point?.date), value: w.end_point?.price },
        ]);
        chartRef.current.overlays.push(series);
        markers.push({
          time: toUnix(w.end_point?.date),
          position: 'aboveBar',
          color: colors.elliott_wave_analysis,
          shape: 'circle',
          text: String(w.wave_number),
        });
      });
    }

    if (layers.includes('structural_edge')) {
      const edges = analysis.structural_edge || [];
      edges.forEach((e) => {
        markers.push({
          time: toUnix(e.date),
          position: 'aboveBar',
          color: colors.structural_edge,
          shape: 'diamond',
          text: e.type,
        });
      });
    }

    if (layers.includes('candlestick_patterns')) {
      const patterns = analysis.candlestick_patterns || [];
      patterns.forEach((p) => {
        markers.push({
          time: toUnix(p.date),
          position: 'aboveBar',
          color: colors.candlestick_patterns,
          shape: 'xCross',
          text: p.type,
        });
      });
    }

    if (layers.includes('divergence_analysis')) {
      const divs = analysis.divergence_analysis || [];
      divs.forEach((d) => {
        markers.push({
          time: toUnix(d.date),
          position: 'aboveBar',
          color: colors.divergence_analysis,
          shape: 'diamond',
          text: d.type,
        });
      });
    }

    if (layers.includes('fair_value_gaps')) {
      const gaps = analysis.fair_value_gaps || [];
      gaps.forEach((g) => {
        const time = toUnix(g.date);
        if (time && g.price_range?.length === 2) {
          const series1 = mainChart.addAreaSeries({
            lineColor: 'rgba(0,255,255,0.3)',
            topColor: 'rgba(0,255,255,0.1)',
            bottomColor: 'rgba(0,255,255,0.1)',
          });
          series1.setData([
            { time, value: g.price_range[0] },
            { time, value: g.price_range[1] },
          ]);
          chartRef.current.overlays.push(series1);
        }
      });
    }

    if (layers.includes('recommendations')) {
      const recs = analysis.recommendations?.trading_strategies || [];
      recs.forEach((r) => {
        markers.push({
          time: toUnix(r.entry_point?.Date),
          position: 'belowBar',
          color: 'green',
          shape: 'arrowUp',
          text: 'Entry',
        });
        markers.push({
          time: toUnix(r.exit_point?.Date),
          position: 'aboveBar',
          color: 'red',
          shape: 'arrowDown',
          text: 'Exit',
        });
      });
    }

    if (layers.includes('anomalous_candles')) {
      const candles = analysis.anomalous_candles || [];
      candles.forEach((c) => {
        markers.push({
          time: toUnix(c.date),
          position: 'aboveBar',
          color: 'yellow',
          shape: 'square',
          text: c.type,
        });
      });
    }

    if (markers.length) {
      candleSeries.setMarkers(
        markers
          .filter((m) => m.time)
          .sort((a, b) => a.time - b.time)
      );
    }

    let panelChart = null;
    let firstPanelSeries = null;
    if (panelLayers.length) {
      panelChart = createChart(panelRef.current, {
        height: 200,
        layout: {
          background: { color: '#121212' },
          textColor:  '#c7c7c7',
        },
        grid: {
          vertLines: { color: '#2a2a2a' },
          horzLines: { color: '#2a2a2a' },
        },
      });
      chartRef.current.panel = panelChart;
      panelChart.applyOptions({ rightPriceScale: { visible: true }, leftPriceScale: { visible: true } });
    }

    const times = data
      .map((c) => toUnix(c['Open Time']))
      .filter((t) => t !== null)
      .sort((a, b) => a - b);
    const buildConstData = (val) => times.map((time) => ({ time, value: val }));

    panelLayers.forEach((layer) => {
      if (!panelChart) return;
      if (layer === 'Volume') {
        const s = addHistogram(panelChart, 'Volume', colors.Volume);
        if (!firstPanelSeries) firstPanelSeries = s;
      } else if (layer === 'MACD') {
        const s1 = addLine(panelChart, 'MACD', colors.MACD);
        if (!firstPanelSeries) firstPanelSeries = s1;
        addLine(panelChart, 'MACD_signal', colors.MACD_signal);
        addHistogram(panelChart, 'MACD_hist', colors.MACD_hist);
      } else if (layer === 'RSI') {
        const s1 = addLine(panelChart, 'RSI', colors.RSI);
        if (!firstPanelSeries) firstPanelSeries = s1;
        const over = panelChart.addLineSeries({ color: 'rgba(255,0,0,0.5)', lineStyle: 2 });
        over.setData(buildConstData(70));
        const under = panelChart.addLineSeries({ color: 'rgba(0,128,0,0.5)', lineStyle: 2 });
        under.setData(buildConstData(30));
      } else {
        const s = addLine(panelChart, layer, colors[layer] || 'black');
        if (!firstPanelSeries) firstPanelSeries = s;
      }
    });

    let cleanup = () => {};
    if (panelChart) {
      const syncTimeRangeFromMain = (range) => {
        panelChart.timeScale().setVisibleRange(range);
      };
      const syncLogicalRangeFromMain = (range) => {
        panelChart.timeScale().setVisibleLogicalRange(range);
      };
      const syncTimeRangeFromPanel = (range) => {
        mainChart.timeScale().setVisibleRange(range);
      };
      const syncLogicalRangeFromPanel = (range) => {
        mainChart.timeScale().setVisibleLogicalRange(range);
      };

      mainChart.timeScale().subscribeVisibleTimeRangeChange(syncTimeRangeFromMain);
      mainChart.timeScale().subscribeVisibleLogicalRangeChange(syncLogicalRangeFromMain);
      panelChart.timeScale().subscribeVisibleTimeRangeChange(syncTimeRangeFromPanel);
      panelChart.timeScale().subscribeVisibleLogicalRangeChange(syncLogicalRangeFromPanel);

      const handleMainCrosshair = (param) => {
        if (param.time === undefined) {
          panelChart.clearCrosshairPosition();
          return;
        }
        if (firstPanelSeries) {
          panelChart.setCrosshairPosition(0, param.time, firstPanelSeries);
        }
      };
      const handlePanelCrosshair = (param) => {
        if (param.time === undefined) {
          mainChart.clearCrosshairPosition();
          return;
        }
        mainChart.setCrosshairPosition(0, param.time, candleSeries);
      };
      mainChart.subscribeCrosshairMove(handleMainCrosshair);
      panelChart.subscribeCrosshairMove(handlePanelCrosshair);
      cleanup = () => {
        mainChart.timeScale().unsubscribeVisibleTimeRangeChange(syncTimeRangeFromMain);
        mainChart.timeScale().unsubscribeVisibleLogicalRangeChange(syncLogicalRangeFromMain);
        panelChart.timeScale().unsubscribeVisibleTimeRangeChange(syncTimeRangeFromPanel);
        panelChart.timeScale().unsubscribeVisibleLogicalRangeChange(syncLogicalRangeFromPanel);
        mainChart.unsubscribeCrosshairMove(handleMainCrosshair);
        panelChart.unsubscribeCrosshairMove(handlePanelCrosshair);
      };
    }

    return () => {
      cleanup();
      if (chartRef.current.overlays) {
        chartRef.current.overlays.forEach((s) => {
          try {
            s.remove();
          } catch (err) {
            console.warn('Ошибка очистки серии', err);
          }
        });
      }
      Object.values(chartRef.current).forEach((ch) => {
        if (typeof ch?.remove === 'function') {
          try {
            ch.remove();
          } catch (err) {
            console.warn('Ошибка очистки графика', err);
          }
        }
      });
      chartRef.current = {};
    };
  }, [data, layers, analysis]);

  const startDrag = (e) => {
    e.preventDefault();
    const startY = e.clientY;
    const startRatio = panelRatio;
    const height = containerRef.current?.getBoundingClientRect().height || 1;
    const onMove = (evt) => {
      const delta = evt.clientY - startY;
      let ratio = startRatio - delta / height;
      ratio = Math.min(0.9, Math.max(0.1, ratio));
      setPanelRatio(ratio);
    };
    const onUp = () => {
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
    };
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
  };

  const panelLayers = layers.filter((l) => panelIndicators.has(l));

  return (
    <div className="chart-panels" ref={containerRef}>
      <div className="legend">
        <span className="legend-item"><span className="legend-color" style={{background:'gray'}}></span>Свечи</span>
        {layers.map((l) => (
          <span key={l} className="legend-item"><span className="legend-color" style={{background:colors[l]||'black'}}></span>{l}</span>
        ))}
      </div>
      <div ref={mainRef} className="chart" style={{flexGrow: 1 - panelRatio}} />
      {panelLayers.length > 0 && (
        <>
          <div className="resize-handle" onMouseDown={startDrag} />
          <div ref={panelRef} className="chart-panel" style={{flexGrow: panelRatio}} />
        </>
      )}
    </div>
  );
}
