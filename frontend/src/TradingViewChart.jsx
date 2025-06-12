// ─────────────────────────────────────────
// src/components/TradingViewChart.jsx
// ─────────────────────────────────────────
import React, { useEffect, useRef, useState, useCallback } from 'react';
import PropTypes from 'prop-types';
import { createChart, CrosshairMode } from 'lightweight-charts';
import { Box } from '@mui/material';

import ChartControls from './ChartControls';
import Legend        from './Legend';

import {
  computeHeikinAshi,
  computeRenko,
  findSRLevels,
  findTrendLines,
} from '../utils/chartUtils';

import { validateAnalysis } from '../data/analysisValidator';

/* ───────────── Helper to build “nice” title from layerKey ─────────── */
const prettify = (key) =>
  key
    .split('_')
    .map((w) => w[0].toUpperCase() + w.slice(1))
    .join(' ');

/* ────────────────────────── COMPONENT ─────────────────────────────── */
export default function TradingViewChart({
  rawPriceData,
  rawVolumeData,
  analysis,
  activeLayers,
  chartType,           // 'candles' | 'heikin' | 'renko'
  resolution,          // минутный / часовой / дневной тайм-фрейм
  onSeriesMetaChange,  // callback для Legend
}) {
  /* ---------- Refs & State ---------- */
  const containerRef = useRef(null);
  const chartRef     = useRef(null);

  // Храним все созданные серии — для будущего скрытия/удаления
  const seriesStore  = useRef({});

  // Прогноз (виртуальные свечи)
  const [forecast, setForecast] = useState(
    analysis?.price_prediction?.virtual_candles ?? []
  );

  /* ─────────────  Stage-1: validate full JSON  ───────────── */
  useEffect(() => {
    if (analysis) validateAnalysis(analysis);
  }, [analysis]);

  /* ─────────────  Stage-1: normalize price & volume  ─────── */
  const priceData  = useMemo(() => {
    if (chartType === 'heikin')  return computeHeikinAshi(rawPriceData);
    if (chartType === 'renko')   return computeRenko(rawPriceData, resolution);
    return rawPriceData;
  }, [rawPriceData, chartType, resolution]);

  const volumeData = rawVolumeData;

  /* ─────────────  INITIALISE LIGHTWEIGHT-CHART  ───────────── */
  useEffect(() => {
    if (!containerRef.current) return;

    chartRef.current = createChart(containerRef.current, {
      width:  containerRef.current.clientWidth,
      height: containerRef.current.clientHeight,
      layout: { backgroundColor: '#ffffff', textColor: '#000' },
      crosshair: { mode: CrosshairMode.Normal },
      rightPriceScale: { scaleMargins: { top: 0.1, bottom: 0.15 } },
      timeScale:      { timeVisible: true },
    });

    // Основные свечи
    const candleSeries = chartRef.current.addCandlestickSeries();
    candleSeries.setData(priceData);
    seriesStore.current.price = candleSeries;

    // Объём
    const volSeries = chartRef.current.addHistogramSeries({
      priceScaleId: '',
      scaleMargins: { top: 0.8, bottom: 0 },
      color: (bar) => (bar.open > bar.close ? '#e74c3c' : '#2ecc71'),
    });
    volSeries.setData(volumeData);
    seriesStore.current.volume = volSeries;

    return () => {
      chartRef.current.remove();
    };
  }, []); // init once

  /* ─────────────  UPDATE price / volume  ───────────── */
  useEffect(() => {
    seriesStore.current.price?.setData(priceData);
  }, [priceData]);
  useEffect(() => {
    seriesStore.current.volume?.setData(volumeData);
  }, [volumeData]);

  /* ─────────────  Stage-1: RENDER FORECAST  ───────────── */
  useEffect(() => {
    // Remove previous forecast
    if (seriesStore.current.forecast) {
      chartRef.current.removeSeries(seriesStore.current.forecast);
      delete seriesStore.current.forecast;
    }
    if (!forecast?.length) return;

    const forecastSeries = chartRef.current.addCandlestickSeries({
      upColor: 'rgba(0,150,0,0.4)',
      downColor: 'rgba(150,0,0,0.4)',
      borderVisible: true,
      priceFormat: { type: 'ohlc' },
      lastValueVisible: false,
    });
    forecastSeries.setData(forecast);
    seriesStore.current.forecast = forecastSeries;

    // Обновляем legend meta
    onSeriesMetaChange?.({
      name: 'Forecast',
      color: 'rgba(0,150,0,0.4)',
      icon: '⧉',
      key: 'forecast',
    });
  }, [forecast]);

  /* ─────────────  Stage-1: RENDER MODEL-ANALYSIS LAYERS  ───────────── */
  const renderModelLayer = useCallback(
    (layerKey) => {
      const dataArr = analysis?.[layerKey];
      if (!dataArr || !activeLayers.includes(layerKey)) return;

      // Helper to register series in store + legend
      const register = (key, series, color, dashed = false, icon = '') => {
        seriesStore.current[key] = series;
        onSeriesMetaChange?.({ name: prettify(key), color, dashed, icon, key });
      };

      /* 1. support_resistance_levels */
      if (layerKey === 'support_resistance_levels') {
        dataArr.forEach((item, idx) => {
          const line = chartRef.current.addLineSeries({
            color: item.type === 'support' ? '#2ecc71' : '#e74c3c',
            lineWidth: 1,
            lineStyle: 0,
          });
          line.setData([
            { time: item.date, value: item.level },
            { time: priceData[priceData.length - 1].time, value: item.level },
          ]);
          register(`${layerKey}_${idx}`, line, line.options().color);
        });
        return;
      }

      /* 2. trend_lines */
      if (layerKey === 'trend_lines') {
        dataArr.forEach((tl, idx) => {
          const { start_point, end_point } = tl;
          const line = chartRef.current.addLineSeries({
            color:
              tl.type === 'ascending'
                ? '#2ecc71'
                : tl.type === 'descending'
                ? '#e74c3c'
                : '#2980b9',
            lineWidth: 2,
          });
          line.setData([
            { time: start_point.date, value: start_point.price },
            { time: end_point.date, value: end_point.price },
          ]);
          register(`${layerKey}_${idx}`, line, line.options().color);
        });
        return;
      }

      /* 3. fibonacci_analysis */
      if (layerKey === 'fibonacci_analysis') {
        dataArr.forEach((fib, idx) => {
          fib.levels.forEach((lvl, L) => {
            const fibLine = chartRef.current.addLineSeries({
              color: lvl.color ?? '#8e44ad',
              lineStyle: 2,
              lineWidth: 1,
            });
            fibLine.setData([
              { time: fib.start_point.date, value: lvl.value },
              { time: fib.end_point.date, value: lvl.value },
            ]);
            register(`${layerKey}_${idx}_${L}`, fibLine, fibLine.options().color, true);
          });
        });
        return;
      }

      /* 4. Зональные слои */
      const zoneLayers = [
        'unfinished_zones',
        'imbalances',
        'fair_value_gaps',
        'gap_analysis',
      ];
      if (zoneLayers.includes(layerKey)) {
        dataArr.forEach((zone, idx) => {
          const zoneSeries = chartRef.current.addAreaSeries({
            topColor: 'rgba(0, 123, 255, 0.2)',
            bottomColor: 'rgba(0, 123, 255, 0.05)',
            lineColor: 'rgba(0, 123, 255, 0.5)',
            lineWidth: 1,
          });

          if (zone.start_point && zone.end_point) {
            zoneSeries.setData([
              { time: zone.start_point.date, value: zone.start_point.price },
              { time: zone.end_point.date, value: zone.end_point.price },
            ]);
          } else if (zone.date && Array.isArray(zone.price_range)) {
            const [low, high] = zone.price_range;
            zoneSeries.setData([
              { time: zone.date, value: low },
              { time: zone.date, value: high },
            ]);
          }
          register(`${layerKey}_${idx}`, zoneSeries, 'rgba(0, 123, 255, 0.5)', false, '▧');
        });
        return;
      }

      /* 5. Маркеры (structural_edge, candlestick_patterns, divergence_analysis) */
      const markerLayers = [
        'structural_edge',
        'candlestick_patterns',
        'divergence_analysis',
      ];
      if (markerLayers.includes(layerKey)) {
        dataArr.forEach((item, idx) => {
          const mSeries = chartRef.current.addLineSeries({ lineWidth: 0 });
          mSeries.setMarkers([
            {
              time: item.date,
              position: 'aboveBar',
              color: '#ff00ff',
              shape: 'circle',
              text: item.type ?? '',
            },
          ]);
          register(`${layerKey}_${idx}`, mSeries, '#ff00ff', false, '●');
        });
      }
    },
    [analysis, activeLayers, priceData, onSeriesMetaChange]
  );

  /* ───────────  RENDER/UPDATE all modelAnalysis layers  ─────────── */
  useEffect(() => {
    // Удаляем старые серии modelAnalysis перед перерендером
    Object.keys(seriesStore.current).forEach((key) => {
      if (
        key.startsWith('support_resistance_levels') ||
        key.startsWith('trend_lines') ||
        key.startsWith('fib') ||
        key.startsWith('unfinished_zones') ||
        key.startsWith('imbalances') ||
        key.startsWith('fair_value_gaps') ||
        key.startsWith('gap_analysis') ||
        key.startsWith('structural_edge') ||
        key.startsWith('candlestick_patterns') ||
        key.startsWith('divergence_analysis')
      ) {
        chartRef.current.removeSeries(seriesStore.current[key]);
        delete seriesStore.current[key];
      }
    });

    // По одному рендерим всё, что выбрано
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

  /* ───────── UI + Controls Wrapper ───────── */
  return (
    <Box sx={{ position: 'relative', width: '100%', height: '100%' }}>
      <Box ref={containerRef} sx={{ width: '100%', height: '100%' }} />
      {/* ChartControls остаётся как был */}
      <ChartControls
        containerRef={containerRef}
        chartRef={chartRef}
        seriesStore={seriesStore}
      />
      {/* Legend */}
      <Legend />
    </Box>
  );
}

TradingViewChart.propTypes = {
  rawPriceData: PropTypes.array.isRequired,
  rawVolumeData: PropTypes.array.isRequired,
  analysis:      PropTypes.object.isRequired,
  activeLayers:  PropTypes.arrayOf(PropTypes.string).isRequired,
  chartType:     PropTypes.oneOf(['candles', 'heikin', 'renko']).isRequired,
  resolution:    PropTypes.string.isRequired,
  onSeriesMetaChange: PropTypes.func,
};
