import React, { useState } from 'react';
import TradingViewChart from './TradingViewChart';
import './App.css';

export default function App() {
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [interval, setInterval] = useState('4h');
  const [limit, setLimit] = useState(144);
  const [token, setToken] = useState(localStorage.getItem('jwt') || '');
  const [data, setData] = useState([]);
  const [layers, setLayers] = useState([]);
  const [availableIndicators, setAvailableIndicators] = useState([]);

  const toggleLayer = (layer) => {
    setLayers((prev) =>
      prev.includes(layer) ? prev.filter((l) => l !== layer) : [...prev, layer]
    );
  };

  const loadData = async () => {
    const body = { symbol, interval, limit, indicators: layers };
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers,
        body: JSON.stringify(body),
      });
      const json = await res.json();
      if (!res.ok) {
        console.error(json);
        alert(json.detail || 'Request error');
        return;
      }
      setData(json.ohlc || []);
      setAvailableIndicators(json.indicators || []);
    } catch (err) {
      console.error(err);
      alert('Network error');
    }
  };

  const saveToken = (val) => {
    setToken(val);
    localStorage.setItem('jwt', val);
  };

  return (
    <div className="container">
      <div className='form-group'>
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
      <div className="form-group">
        {availableIndicators.map((ind) => (
          <label key={ind} style={{ marginRight: '10px' }}>
            <input
              type="checkbox"
              checked={layers.includes(ind)}
              onChange={() => toggleLayer(ind)}
            />
            {ind}
          </label>
        ))}
      </div>
      <div className="chart-container">
        <TradingViewChart data={data} layers={layers} />
      </div>
    </div>
  );
}
