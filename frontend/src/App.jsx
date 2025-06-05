import React, { useState } from 'react';
import TradingViewChart from './TradingViewChart';

export default function App() {
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [interval, setInterval] = useState('4h');
  const [limit, setLimit] = useState(144);
  const [token, setToken] = useState(localStorage.getItem('jwt') || '');
  const [data, setData] = useState([]);
  const [layers, setLayers] = useState(['volume']);

  const toggleLayer = (layer) => {
    setLayers((prev) =>
      prev.includes(layer) ? prev.filter((l) => l !== layer) : [...prev, layer]
    );
  };

  const loadData = async () => {
    const body = { symbol, interval, limit, indicators: [] };
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    });
    const json = await res.json();
    setData(json.ohlc || []);
  };

  const saveToken = (val) => {
    setToken(val);
    localStorage.setItem('jwt', val);
  };

  return (
    <div>
      <div style={{ marginBottom: '10px' }}>
        <input value={symbol} onChange={(e) => setSymbol(e.target.value)} placeholder="Symbol" />
        <select value={interval} onChange={(e) => setInterval(e.target.value)}>
          <option value="1h">1h</option>
          <option value="4h">4h</option>
          <option value="1d">1d</option>
        </select>
        <input type="number" value={limit} onChange={(e) => setLimit(Number(e.target.value))} />
        <input
          style={{ width: '300px' }}
          placeholder="JWT token"
          value={token}
          onChange={(e) => saveToken(e.target.value)}
        />
        <button onClick={loadData}>Load</button>
      </div>
      <div style={{ marginBottom: '10px' }}>
        <label>
          <input
            type="checkbox"
            checked={layers.includes('volume')}
            onChange={() => toggleLayer('volume')}
          />
          Volume
        </label>
        <label>
          <input
            type="checkbox"
            checked={layers.includes('ma50')}
            onChange={() => toggleLayer('ma50')}
          />
          MA 50
        </label>
        <label>
          <input
            type="checkbox"
            checked={layers.includes('ma200')}
            onChange={() => toggleLayer('ma200')}
          />
          MA 200
        </label>
      </div>
      <TradingViewChart data={data} layers={layers} />
    </div>
  );
}
