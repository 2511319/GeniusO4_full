import React, { useState, useRef, useEffect } from 'react';
import { createChart } from 'lightweight-charts';

export default function App() {
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [interval, setInterval] = useState('1h');
  const [limit, setLimit] = useState(100);
  const [analysis, setAnalysis] = useState('');
  const chartRef = useRef(null);
  const seriesRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    chartRef.current = createChart(containerRef.current, { width: 600, height: 400 });
    seriesRef.current = chartRef.current.addCandlestickSeries();
    return () => chartRef.current.remove();
  }, []);

  async function handleAnalyze() {
    try {
      const resp = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol, interval, limit })
      });
      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}`);
      }
      const data = await resp.json();
      const candles = (data.ohlc || []).map(c => ({
        time: Math.floor(new Date(c['Open Time']).getTime() / 1000),
        open: parseFloat(c.Open),
        high: parseFloat(c.High),
        low: parseFloat(c.Low),
        close: parseFloat(c.Close)
      }));
      seriesRef.current.setData(candles);
      setAnalysis(JSON.stringify(data.analysis, null, 2));
    } catch (err) {
      console.error('Analyze failed', err);
    }
  }

  return (
    <div style={{ padding: '1rem' }}>
      <div>
        <label>
          Тикер:
          <input value={symbol} onChange={e => setSymbol(e.target.value)} />
        </label>
      </div>
      <div>
        <label>
          Интервал:
          <select value={interval} onChange={e => setInterval(e.target.value)}>
            <option value="1m">1m</option>
            <option value="5m">5m</option>
            <option value="15m">15m</option>
            <option value="1h">1h</option>
            <option value="4h">4h</option>
            <option value="1d">1d</option>
          </select>
        </label>
      </div>
      <div>
        <label>
          Количество свечей:
          <input type="number" value={limit} min="1" onChange={e => setLimit(Number(e.target.value))} />
        </label>
      </div>
      <button onClick={handleAnalyze}>Анализ</button>

      <div ref={containerRef} style={{ width: '100%', height: '500px' }} />
      {analysis && (
        <pre style={{ whiteSpace: 'pre-wrap' }}>{analysis}</pre>
      )}
    </div>
  );
}
