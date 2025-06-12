// src/components/TradingViewChart.jsx

import React, {
  useEffect,
  useRef,
  useMemo,
  useState,
  useCallback,
} from 'react';
import PropTypes from 'prop-types';
import { createChart, CrosshairMode } from 'lightweight-charts';
import { Box } from '@mui/material';

import ChartControls from './ChartControls';
import Legend        from './Legend';

import { validateAnalysis } from '../data/analysisValidator';
import {
  computeHeikinAshi,
  computeRenko,
} from '../utils/chartUtils';

/** Преобразование ключей в читабельный заголовок */
const prettify = key =>
  key
    .split('_')
    .map(w => w[0].toUpperCase() + w.slice(1))
    .join(' ');

export default function TradingViewChart({
  rawPriceData,
  rawVolumeData,
  analysis,
  activeLayers,
  chartType,
  resolution,
  onSeriesMetaChange,
}) {
  const containerRef   = useRef(null);
  const chartRef       = useRef(null);
  const seriesStore    = useRef({});

  // Forecast (виртуальные свечи)
  const [forecast]     = useState(analysis.price_prediction?.virtual_candles || []);

  // 1. Валидируем полный ответ модели
  useEffect(() => {
    if (analysis) validateAnalysis(analysis);
  }, [analysis]);

  // 2. Готовим priceData в зависимости от типа графика
  const priceData = useMemo(() => {
    if (chartType === 'heikin') return computeHeikinAshi(rawPriceData);
    if (chartType === 'renko')  return computeRenko(rawPriceData, resolution);
    return rawPriceData;
  }, [rawPriceData, chartType, resolution]);

  // 3. Инициализация chart и price/volume серий
  useEffect(() => {
    if (!containerRef.current) return;
    chartRef.current = createChart(containerRef.current, {
      layout: { backgroundColor: '#ffffff', textColor: '#000000' },
      crosshair: { mode: CrosshairMode.Normal },
      rightPriceScale: { scaleMargins: { top: 0.1, bottom: 0.15 } },
      timeScale:      { timeVisible: true },
      width:  containerRef.current.clientWidth,
      height: containerRef.current.clientHeight,
    });

    // Основные свечи
    const priceSeries = chartRef.current.addCandlestickSeries();
    priceSeries.setData(priceData);
    seriesStore.current.price = priceSeries;

    // Объём
    const volSeries = chartRef.current.addHistogramSeries({
      priceScaleId: '',
      scaleMargins: { top: 0.8, bottom: 0 },
      color: bar => (bar.open > bar.close ? '#e74c3c' : '#2ecc71'),
    });
    volSeries.setData(rawVolumeData);
    seriesStore.current.volume = volSeries;

    return () => chartRef.current.remove();
  }, []);

  // 4. Обновление price/volume при изменении данных
  useEffect(() => { seriesStore.current.price?.setData(priceData); }, [priceData]);
  useEffect(() => { seriesStore.current.volume?.setData(rawVolumeData); }, [rawVolumeData]);

  // 5. Рендер Forecast-серии
  useEffect(() => {
    // Удаляем старую серию, если есть
    if (seriesStore.current.forecast) {
      chartRef.current.removeSeries(seriesStore.current.forecast);
      delete seriesStore.current.forecast;
    }
    // Если прогноз есть, рисуем
    if (forecast.length) {
      const fs = chartRef.current.addCandlestickSeries({
        upColor:   'rgba(0,150,0,0.4)',
        downColor: 'rgba(150,0,0,0.4)',
        borderVisible: true,
        priceFormat: { type: 'ohlc' },
        lastValueVisible: false,
      });
      fs.setData(forecast);
      seriesStore.current.forecast = fs;
      onSeriesMetaChange?.({
        key:   'price_prediction',
        name:  'Forecast',
        color: 'rgba(0,150,0,0.4)',
        icon:  '⧉',
      });
    }
  }, [forecast]);

  // 6. Рендер технических overlay (MA, VWAP, Bollinger, Envelope, SAR, Ichimoku)
  useEffect(() => {
    const ind = analysis;
    const register = (key, series, color, dashed = false, icon = '') => {
      seriesStore.current[key] = series;
      onSeriesMetaChange?.({ key, name: prettify(key), color, dashed, icon });
    };

    // Сначала удаляем старые overlay-серии
    Object.keys(seriesStore.current)
      .filter(k =>
        ['MA_','VWAP','Bollinger','Moving_Average_Envelope','Parabolic_SAR','Ichimoku_'].some(prefix => k.startsWith(prefix))
      )
      .forEach(k => {
        chartRef.current.removeSeries(seriesStore.current[k]);
        delete seriesStore.current[k];
      });

    // MA lines
    const maConfig = {
      MA_20:  { color: '#2979ff', width: 1, style: 0 },
      MA_50:  { color: '#0288d1', width: 1, style: 2 },
      MA_100: { color: '#0277bd', width: 1, style: 3 },
      MA_200: { color: '#01579b', width: 2, style: 0 },
    };
    Object.entries(maConfig).forEach(([key, opt]) => {
      if (activeLayers.includes(key) && Array.isArray(ind[key])) {
        const series = chartRef.current.addLineSeries({
          color: opt.color, lineWidth: opt.width, lineStyle: opt.style,
        });
        series.setData(ind[key].map(p => ({ time: p.date, value: p.value })));
        register(key, series, opt.color, opt.style !== 0);
      }
    });

    // VWAP
    if (activeLayers.includes('VWAP') && Array.isArray(ind.VWAP)) {
      const s = chartRef.current.addLineSeries({ color: '#ff9800', lineWidth: 1 });
      s.setData(ind.VWAP.map(p => ({ time: p.date, value: p.value })));
      register('VWAP', s, '#ff9800');
    }

    // Bollinger Bands (lines)
    ['Middle','Upper','Lower'].forEach(pos => {
      const key = `Bollinger_${pos}`;
      if (activeLayers.includes(key) && Array.isArray(ind[key])) {
        const color = pos==='Middle'? '#9e9e9e' : '#bdbdbd';
        const style = pos==='Middle'? 0 : 2;
        const s = chartRef.current.addLineSeries({ color, lineWidth: 1, lineStyle: style });
        s.setData(ind[key].map(p => ({ time: p.date, value: p.value })));
        register(key, s, color, style !== 0);
      }
    });

    // Moving Average Envelope
    ['Moving_Average_Envelope_Upper','Moving_Average_Envelope_Lower'].forEach(key => {
      if (activeLayers.includes(key) && Array.isArray(ind[key])) {
        const color = '#4caf50';
        const s = chartRef.current.addLineSeries({ color, lineWidth: 1, lineStyle: 2 });
        s.setData(ind[key].map(p => ({ time: p.date, value: p.value })));
        register(key, s, color, true);
      }
    });

    // Parabolic SAR (markers)
    if (activeLayers.includes('Parabolic_SAR') && Array.isArray(ind.Parabolic_SAR)) {
      const s = chartRef.current.addLineSeries({ lineWidth: 0 });
      s.setMarkers(ind.Parabolic_SAR.map(p => ({
        time: p.date,
        position: p.value > priceData[priceData.length-1].low ? 'aboveBar' : 'belowBar',
        color: '#ffeb3b',
        shape: 'circle',
      })));
      register('Parabolic_SAR', s, '#ffeb3b', false, '•');
    }

    // Ichimoku (lines + cloud)
    if (activeLayers.includes('Ichimoku_Conversion_Line') && Array.isArray(ind.Ichimoku_Conversion_Line)) {
      const s = chartRef.current.addLineSeries({ color: '#d32f2f', lineWidth: 1 });
      s.setData(ind.Ichimoku_Conversion_Line.map(p => ({ time: p.date, value: p.value })));
      register('Ichimoku_Conversion_Line', s, '#d32f2f');
    }
    if (activeLayers.includes('Ichimoku_Base_Line') && Array.isArray(ind.Ichimoku_Base_Line)) {
      const s = chartRef.current.addLineSeries({ color: '#1976d2', lineWidth: 1 });
      s.setData(ind.Ichimoku_Base_Line.map(p => ({ time: p.date, value: p.value })));
      register('Ichimoku_Base_Line', s, '#1976d2');
    }
    if (
      activeLayers.includes('Ichimoku_A') &&
      activeLayers.includes('Ichimoku_B') &&
      Array.isArray(ind.Ichimoku_A) &&
      Array.isArray(ind.Ichimoku_B)
    ) {
      const cloud = chartRef.current.addAreaSeries({
        topColor:    'rgba(156,39,176,0.2)',
        bottomColor: 'rgba(156,39,176,0.05)',
        lineColor:   'rgba(156,39,176,0.6)',
      });
      // Merge A and B: use A values, cloud fills to baseline representing B
      const data = ind.Ichimoku_A.map((p, i) => ({
        time:  p.date,
        value: p.value,
        // areaSeries cannot take dual values, but visually acceptable
      }));
      cloud.setData(data);
      register('Ichimoku_Cloud', cloud, 'rgba(156,39,176,0.6)', false, '▧');
    }
  }, [analysis, activeLayers, priceData, rawVolumeData]);

  // 7. Рендер modelAnalysis слоёв
  const renderModelLayer = useCallback((layer) => {
    const arr = analysis[layer];
    if (!activeLayers.includes(layer) || !Array.isArray(arr)) return;
    const register = (key, series, color, dashed = false, icon = '') => {
      seriesStore.current[key] = series;
      onSeriesMetaChange?.({ key, name: prettify(key), color, dashed, icon });
    };

    // support_resistance_levels
    if (layer === 'support_resistance_levels') {
      arr.forEach((it, i) => {
        const s = chartRef.current.addLineSeries({
          color: it.type === 'support' ? 'green' : 'red',
          lineWidth: 1,
        });
        s.setData([
          { time: it.date, value: it.level },
          { time: priceData[priceData.length-1].time, value: it.level },
        ]);
        register(`${layer}_${i}`, s, s.options().color, false, '─');
      });
      return;
    }

    // trend_lines
    if (layer === 'trend_lines') {
      arr.forEach((it, i) => {
        const s = chartRef.current.addLineSeries({
          color: it.type === 'ascending' ? 'green' : 'red',
          lineWidth: 2,
        });
        s.setData([
          { time: it.start_point.date, value: it.start_point.price },
          { time: it.end_point.date,   value: it.end_point.price },
        ]);
        register(`${layer}_${i}`, s, s.options().color, false, '─');
      });
      return;
    }

    // fibonacci_analysis
    if (layer === 'fibonacci_analysis') {
      arr.forEach((fib, i) => {
        fib.levels.forEach((lvl, j) => {
          const s = chartRef.current.addLineSeries({
            color: lvl.color,
            lineStyle: 2,
            lineWidth: 1,
          });
          s.setData([
            { time: fib.start_point.date, value: lvl.value },
            { time: fib.end_point.date,   value: lvl.value },
          ]);
          register(`${layer}_${i}_${j}`, s, lvl.color, true, '─');
        });
      });
      return;
    }

    // Зональные слои
    ['unfinished_zones','imbalances','fair_value_gaps','gap_analysis'].forEach(zKey => {
      if (layer !== zKey) return;
      arr.forEach((z, i) => {
        const s = chartRef.current.addAreaSeries({
          topColor:    'rgba(0,123,255,0.2)',
          bottomColor: 'rgba(0,123,255,0.05)',
          lineColor:   'rgba(0,123,255,0.5)',
          lineWidth: 1,
        });
        if (z.start_point && z.end_point) {
          s.setData([
            { time: z.start_point.date, value: z.start_point.price },
            { time: z.end_point.date,   value: z.end_point.price },
          ]);
        } else if (z.date && Array.isArray(z.price_range)) {
          const [low, high] = z.price_range;
          s.setData([
            { time: z.date, value: low },
            { time: z.date, value: high },
          ]);
          console.warn(`Missing start/end for ${layer}[${i}], used price_range fallback`);
        }
        register(`${layer}_${i}`, s, 'rgba(0,123,255,0.5)', false, '▧');
      });
    });

    // structural_edge, candlestick_patterns, divergence_analysis (markers)
    ['structural_edge','candlestick_patterns','divergence_analysis'].forEach(mKey => {
      if (layer !== mKey) return;
      arr.forEach((it, i) => {
        const s = chartRef.current.addLineSeries({ lineWidth: 0 });
        s.setMarkers([{
          time:     it.date,
          position: 'aboveBar',
          color:    '#ff00ff',
          shape:    'circle',
          text:     it.type[0] || '',
        }]);
        register(`${layer}_${i}`, s, '#ff00ff', false, '●');
      });
    });
  }, [analysis, activeLayers, priceData, onSeriesMetaChange]);

  // Применяем renderModelLayer для всех modelAnalysis слоёв
  useEffect(() => {
    // Удаляем старые modelAnalysis-серии
    Object.keys(seriesStore.current)
      .filter(k => /^[a-z_]+_\d/.test(k))
      .forEach(k => {
        chartRef.current.removeSeries(seriesStore.current[k]);
        delete seriesStore.current[k];
      });
    // Рендерим заново
    [
      'support_resistance_levels',
      'trend_lines',
      'fibonacci_analysis',
      'unfinished_zones',
      'imbalances',
      'fair_value_gaps',
      'gap_analysis',
      'structural_edge',
      'candlestick_patterns',
      'divergence_analysis',
    ].forEach(renderModelLayer);
  }, [analysis, activeLayers, renderModelLayer]);

  return (
    <Box sx={{ position: 'relative', width: '100%', height: '100%' }}>
      <Box ref={containerRef} sx={{ width: '100%', height: '100%' }} />
      <ChartControls
        containerRef={containerRef}
        chartRef={chartRef}
        seriesStore={seriesStore}
      />
      <Legend />
    </Box>
  );
}

TradingViewChart.propTypes = {
  rawPriceData:      PropTypes.array.isRequired,
  rawVolumeData:     PropTypes.array.isRequired,
  analysis:          PropTypes.object.isRequired,
  activeLayers:      PropTypes.arrayOf(PropTypes.string).isRequired,
  chartType:         PropTypes.oneOf(['candles','heikin','renko']).isRequired,
  resolution:        PropTypes.string.isRequired,
  onSeriesMetaChange:PropTypes.func,
};
