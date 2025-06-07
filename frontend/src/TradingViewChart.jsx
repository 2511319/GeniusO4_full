import React, { useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';
import { Box } from '@mui/material';
import ChartControls from './ChartControls';
import { computeHeikinAshi, computeRenko, findSRLevels } from './chartUtils';

export default function TradingViewChart({ data, layers }) {
  const containerRef = useRef();
  const chartRef     = useRef();
  const seriesRef    = useRef();
  const tooltipRef   = useRef();
  const [type, setType] = React.useState('candles');

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

  /* ───────── update series on data | type ───────── */
  useEffect(() => {
    if (!chartRef.current) return;

    const chart = chartRef.current;
    if (seriesRef.current) {
      try {
        chart.removeSeries(seriesRef.current);
      } catch (_) {}
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
    seriesRef.current = series;

    /* support/resistance */
    const levels = findSRLevels(processed);
    levels.forEach(({ price, type }) =>
      series.createPriceLine({
        price,
        lineWidth: 1,
        color: type === 'support' ? '#4caf50' : '#f44336',
        lineStyle: 2,
      }),
    );

    /* tooltip */
    chart.subscribeCrosshairMove((param) => {
      if (!param || !param.time || !param.seriesData.size) {
        tooltipRef.current.style.display = 'none';
        return;
      }
      const datum = param.seriesData.get(series);
      if (!datum) return;
      const { value } = datum;
      const { rsi, macd } = param.seriesData.values().next().value || {};
      tooltipRef.current.innerHTML = `
        <div><b>${new Date(param.time * 1000).toLocaleString()}</b></div>
        O: ${value.open.toFixed(2)} H: ${value.high.toFixed(2)}
        L: ${value.low.toFixed(2)} C: ${value.close.toFixed(2)}<br/>
        ${rsi ? `RSI: ${rsi.toFixed(2)} ` : ''}
        ${macd ? `MACD: ${macd.toFixed(2)}` : ''}
      `;
      tooltipRef.current.style.display = 'block';
      tooltipRef.current.style.left = param.point.x + 10 + 'px';
      tooltipRef.current.style.top  = param.point.y + 10 + 'px';
    });
  }, [data, type]);

  return (
    <Box sx={{ height: '100%', position: 'relative' }}>
      <ChartControls type={type} onChange={setType} />
      <Box ref={containerRef} sx={{ height: '100%' }} />
    </Box>
  );
}
