import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { TextField, Button, Select, MenuItem, Box, FormControlLabel, Checkbox } from '@mui/material';
import TradingViewChart from '../TradingViewChart';
import { setToken } from '../store';
import '../App.css';

export default function Home() {
  const dispatch = useDispatch();
  const token = useSelector((state) => state.auth.token);
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [interval, setInterval] = useState('4h');
  const [limit, setLimit] = useState(144);
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
      console.log('Запрос к /api/analyze', body);
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers,
        body: JSON.stringify(body),
      });
      console.log('Код ответа', res.status);
      const json = await res.json();
      console.log('Ответ API', json);
      if (!res.ok) {
        console.error('Ошибка API', json);
        alert(json.detail || 'Request error');
        return;
      }
      const ohlc = json.ohlc || [];
      setData(ohlc);
      setAvailableIndicators(json.indicators || []);
      console.log('Данных получено:', ohlc.length);
    } catch (err) {
      console.error(err);
      alert('Network error');
    }
  };

  const saveToken = (val) => {
    dispatch(setToken(val));
  };

  return (
    <Box className="container">
      <Box className="form-group" sx={{ display: 'flex', gap: 1 }}>
        <TextField label="Symbol" value={symbol} onChange={(e) => setSymbol(e.target.value)} />
        <Select value={interval} onChange={(e) => setInterval(e.target.value)}>
          <MenuItem value="1h">1h</MenuItem>
          <MenuItem value="4h">4h</MenuItem>
          <MenuItem value="1d">1d</MenuItem>
        </Select>
        <TextField type="number" label="Limit" value={limit} onChange={(e) => setLimit(Number(e.target.value))} />
        <TextField
          label="JWT token"
          sx={{ width: 300 }}
          value={token}
          onChange={(e) => saveToken(e.target.value)}
        />
        <Button variant="contained" onClick={loadData} type="button">Load</Button>
      </Box>
      <Box className="form-group">
        {availableIndicators.map((ind) => (
          <FormControlLabel
            key={ind}
            control={<Checkbox checked={layers.includes(ind)} onChange={() => toggleLayer(ind)} />}
            label={ind}
          />
        ))}
      </Box>
      <Box className="chart-container">
        <TradingViewChart data={data} layers={layers} />
      </Box>
    </Box>
  );
}
