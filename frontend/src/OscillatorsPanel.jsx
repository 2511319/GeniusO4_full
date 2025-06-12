import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { createChart } from 'lightweight-charts';

/**
 * OscillatorsPanel рендерит три осциллятора:
 * - RSI
 * - Stochastic (%K и %D)
 * - Williams %R
 *
 * Каждый осциллятор в своей панели.
 *
 * Props:
 * - rsi:        Array<{ time: string|number, value: number }>
 * - stochastic: { k: Array<{ time, value }>, d: Array<{ time, value }> }
 * - williams:   Array<{ time: string|number, value: number }>
 */
export default function OscillatorsPanel({ rsi, stochastic, williams }) {
  const rsiRef = useRef();
  const stoRef = useRef();
  const wilRef = useRef();

  useEffect(() => {
    // RSI chart
    rsiRef.current = createChart(document.getElementById('rsi-chart'), {
      width: document.getElementById('rsi-chart').clientWidth,
      height: 120,
      layout: { backgroundColor: '#fff', textColor: '#000' },
      rightPriceScale: { scaleMargins: { top: 0.3, bottom: 0 } },
      timeScale: { timeVisible: true },
    });
    const rsiSeries = rsiRef.current.addLineSeries({ color: '#ff5722' });
    rsiSeries.setData(rsi);
    rsiRef.current.applyOptions({
      layout: { backgroundColor: '#f9f9f9' },
      grid: { horzLines: { color: '#eee' } },
    });

    // Stochastic chart
    stoRef.current = createChart(document.getElementById('sto-chart'), {
      width: document.getElementById('sto-chart').clientWidth,
      height: 120,
      layout: { backgroundColor: '#fff', textColor: '#000' },
      rightPriceScale: { scaleMargins: { top: 0.3, bottom: 0 } },
      timeScale: { timeVisible: true },
    });
    const kSeries = stoRef.current.addLineSeries({ color: '#2962ff' });
    const dSeries = stoRef.current.addLineSeries({ color: '#c62828' });
    kSeries.setData(stochastic.k);
    dSeries.setData(stochastic.d);

    // Williams chart
    wilRef.current = createChart(document.getElementById('wil-chart'), {
      width: document.getElementById('wil-chart').clientWidth,
      height: 120,
      layout: { backgroundColor: '#fff', textColor: '#000' },
      rightPriceScale: { scaleMargins: { top: 0.3, bottom: 0 } },
      timeScale: { timeVisible: true },
    });
    const wilSeries = wilRef.current.addLineSeries({ color: '#00796b' });
    wilSeries.setData(williams);

    return () => {
      rsiRef.current.remove();
      stoRef.current.remove();
      wilRef.current.remove();
    };
  }, [rsi, stochastic, williams]);

  return (
    <div style={{ width: '100%' }}>
      <div id="rsi-chart" style={{ marginBottom: 8 }} />
      <div id="sto-chart" style={{ marginBottom: 8 }} />
      <div id="wil-chart" />
    </div>
  );
}

OscillatorsPanel.propTypes = {
  rsi: PropTypes.array.isRequired,
  stochastic: PropTypes.shape({
    k: PropTypes.array.isRequired,
    d: PropTypes.array.isRequired,
  }).isRequired,
  williams: PropTypes.array.isRequired,
};
