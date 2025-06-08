import React, { useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';
import { Box } from '@mui/material';
import ChartControls from './ChartControls';
import Legend from './Legend';
import { computeHeikinAshi, computeRenko, findSRLevels, findTrendLines } from './chartUtils';

export default function TradingViewChart({ data, patterns = [], layers, showSR = false, showTrends = false }) {
  const containerRef = useRef();
  const chartRef     = useRef();
  const seriesRef    = useRef();
  const tooltipRef   = useRef();
  const indicatorSeriesRef = useRef({});
  const seriesInfoRef = useRef({});
  const crosshairHandlerRef = useRef();
  const [type, setType] = React.useState('candles');
  const [legendItems, setLegendItems] = React.useState([]);

  /* ───────── helpers for indicators tooltip ───────── */
  const buildTooltip = () => {
    const node = document.createElement('div');
    node.style.position = 'absolute';
    node.style.pointerEvents = 'none';
    node.style.background = 'rgba(0,0,0,0.8)';
    node.style.color = '#fff';
    node.style.padding = '6px 8px';
    node.style.fontSize = '12px';
    node.style.borderRadius = '4px';
    node.style.zIndex = 100;
    containerRef.current.appendChild(node);
    return node;
  };

  /* ───────── create chart once ───────── */
  useEffect(() => {
    chartRef.current = createChart(containerRef.current, {
      layout: {
        background: { color: '#121212' },
        textColor:  '#c7c7c7',
      },
      grid: {
        vertLines: { color: '#2a2a2a' },
        horzLines: { color: '#2a2a2a' },
      },
      width:  containerRef.current.clientWidth,
      height: containerRef.current.clientHeight,
      crosshair: { mode: 1 },
      localization: { locale: 'ru-RU' },
    });

    tooltipRef.current = buildTooltip();

    const resize = () =>
      chartRef.current.resize(
        containerRef.current.clientWidth,
        containerRef.current.clientHeight,
      );
    window.addEventListener('resize', resize);

    return () => {
      window.removeEventListener('resize', resize);
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
    };
  }, []);

  /* ───────── update series on data | type | layers ───────── */
  useEffect(() => {
    if (!chartRef.current) return;

    const chart = chartRef.current;
    if (seriesRef.current) {
      try {
        chart.removeSeries(seriesRef.current);
      } catch (_) {}
    }
    Object.values(indicatorSeriesRef.current).forEach((s) => {
      try { chart.removeSeries(s); } catch (_) {}
    });
    indicatorSeriesRef.current = {};
    seriesInfoRef.current = {};
    if (crosshairHandlerRef.current) {
      chart.unsubscribeCrosshairMove(crosshairHandlerRef.current);
    }

    const prepare = () => {
      if (type === 'heikin') return computeHeikinAshi(data);
      if (type === 'renko')  return computeRenko(data);
      return data;
    };

    const processed = prepare() || [];
    if (!processed.length) {
      seriesRef.current = null;
      return;
    }
    const series = chart.addCandlestickSeries();
    series.setData(processed);
    chart.timeScale().fitContent();
    seriesRef.current = series;

    /* indicator lines */
    const colorMap = {
      RSI: '#ff9800',
      MACD: '#2196f3',
      OBV: '#9c27b0',
      ATR: '#009688',
      VWAP: '#795548'
    };
    layers.forEach((name, idx) => {
      if (!processed[0] || processed[0][name] === undefined) return;
      const color = colorMap[name] || `hsl(${idx*60},70%,50%)`;
      const line = chart.addLineSeries({ color });
      line.setData(processed.map((d) => ({ time: d.time, value: d[name] })));
      indicatorSeriesRef.current[name] = line;
      seriesInfoRef.current[name] = { series: line, color, dashed: false };
    });

    /* support/resistance */
    if (showSR) {
      const levels = findSRLevels(processed);
      let hasSupport = false;
      let hasResistance = false;
      levels.forEach(({ price, type, time }) => {
        const color = type === 'support' ? '#4caf50' : '#f44336';
        if (type === 'support') hasSupport = true; else hasResistance = true;
        series.createRay({
          price,
          time,
          extend: 'right',
          lineWidth: 1,
          color,
          lineStyle: 2,
        });
      });
      if (hasSupport) seriesInfoRef.current.support = { color: '#4caf50', dashed: true };
      if (hasResistance) seriesInfoRef.current.resistance = { color: '#f44336', dashed: true };
    }

    /* trend lines */
    if (showTrends) {
      const tl = findTrendLines(processed);
      let hasSupport = false;
      let hasResistance = false;
      tl.forEach(({ from, to, type }) => {
        const color = type === 'support' ? '#4caf50' : '#f44336';
        if (type === 'support') hasSupport = true; else hasResistance = true;
        series.createRay({
          points: [
            { time: from.time, value: from.price },
            { time: to.time, value: to.price },
          ],
          extend: 'right',
          lineWidth: 1,
          color,
          lineStyle: 0,
        });
      });
      if (hasSupport) seriesInfoRef.current['trend-support'] = { color: '#4caf50', dashed: false };
      if (hasResistance) seriesInfoRef.current['trend-resistance'] = { color: '#f44336', dashed: false };
    }

    if (layers.includes('candlestick_patterns') && patterns.length) {
      const markers = patterns.map((p) => ({
        time: p.time,
        position: 'aboveBar',
        color: 'magenta',
        shape: 'cross',
        text: p.type || '',
      }));
      series.setMarkers(markers);
      seriesInfoRef.current.patterns = { color: 'magenta', dashed: false };
    }

    /* tooltip */
    const handler = (param) => {
      if (!param || !param.time || !param.seriesData.size) {
        tooltipRef.current.style.display = 'none';
        return;
      }
      const datum = param.seriesData.get(series);
      if (!datum) return;
      const { value } = datum;
      const indVals = Object.entries(indicatorSeriesRef.current)
        .map(([name, s]) => {
          const v = param.seriesData.get(s);
          return v ? `${name}: ${Number(v.value).toFixed(2)}` : '';
        })
        .filter(Boolean)
        .join(' ');
      tooltipRef.current.innerHTML = `
        <div><b>${new Date(param.time * 1000).toLocaleString()}</b></div>
        O: ${value.open.toFixed(2)} H: ${value.high.toFixed(2)}
        L: ${value.low.toFixed(2)} C: ${value.close.toFixed(2)}<br/>
        ${indVals}
      `;
      tooltipRef.current.style.display = 'block';
      tooltipRef.current.style.left = param.point.x + 10 + 'px';
      tooltipRef.current.style.top  = param.point.y + 10 + 'px';
    };
    chart.subscribeCrosshairMove(handler);
    crosshairHandlerRef.current = handler;

    setLegendItems(
      Object.entries(seriesInfoRef.current).map(([name, info]) => ({
        name,
        color: info.color,
        dashed: info.dashed,
      }))
    );
  }, [data, type, layers, showSR, showTrends, patterns]);

  return (
    <Box sx={{ height: '100%', position: 'relative' }}>
      <Legend items={legendItems} />
      <ChartControls type={type} onChange={setType} />
      <Box ref={containerRef} sx={{ height: '100%' }} />
    </Box>
  );
}
