import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import {
  Container, Grid, Paper, Box,
  TextField, Select, MenuItem, Button, Typography,
  Divider, FormGroup, FormControlLabel, Checkbox,
} from '@mui/material';

import TradingViewChart       from '../TradingViewChart';
import AnalysisSections        from '../AnalysisSections';
import TechnicalIndicators     from '../TechnicalIndicators';
import AdvancedIndicators      from '../AdvancedIndicators';
import ModelAnalysisIndicators from '../ModelAnalysisIndicators';

export default function Home() {
  const token = useSelector((state) => state.auth.token);

  const [symbol,  setSymbol]  = useState('BTCUSDT');
  const [interval,setInterval]= useState('4h');
  const [limit,   setLimit]   = useState(144);
  const [layers,  setLayers]  = useState(['RSI']);
  const [data,    setData]    = useState([]);
  const [analysis,setAnalysis]= useState(null);
  const [available,setAvailable]= useState([]);

  const toggleLayer = (name) =>
    setLayers((prev) =>
      prev.includes(name) ? prev.filter((l) => l !== name) : [...prev, name]);

  const loadData = async () => {
    const body = { symbol, interval, limit, indicators: layers };
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers.Authorization = `Bearer ${token}`;

    const res   = await fetch('/api/analyze', {
      method:'POST', headers, body:JSON.stringify(body),
    });
    const json  = await res.json();
    setAnalysis(json.analysis);
    setData(json.ohlc);
    setAvailable(json.indicators || []);
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 2 }}>
      <Grid container spacing={2}>
        {/* левая панель */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom>Параметры запроса</Typography>

            <TextField
              fullWidth label="Тикер"
              value={symbol} onChange={(e) => setSymbol(e.target.value)}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth type="number" label="Количество свечей"
              value={limit} onChange={(e) => setLimit(+e.target.value)}
              sx={{ mb: 2 }}
            />

            <Select
              fullWidth value={interval} label="Таймфрейм"
              onChange={(e) => setInterval(e.target.value)}
              sx={{ mb: 2 }}
            >
              {['1m','5m','15m','1h','4h','1d'].map((tf) => (
                <MenuItem key={tf} value={tf}>{tf}</MenuItem>
              ))}
            </Select>

            <Button variant="contained" fullWidth onClick={loadData}>
              Запустить анализ
            </Button>
          </Paper>

          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle1">Индикаторы графика</Typography>
            <Divider sx={{ mb: 2 }} />

            <FormGroup>
              {['RSI','MACD','OBV','ATR','VWAP'].map((ind) => (
                <FormControlLabel
                  key={ind}
                  control={
                    <Checkbox
                      checked={layers.includes(ind)}
                      onChange={() => toggleLayer(ind)}
                    />
                  }
                  label={ind}
                />
              ))}
            </FormGroup>
          </Paper>

          <Paper sx={{ p: 2, mb: 2 }}>
            <TechnicalIndicators
              available={available}
              layers={layers}
              toggleLayer={toggleLayer}
            />
          </Paper>

          <Paper sx={{ p: 2, mb: 2 }}>
            <AdvancedIndicators
              available={available}
              layers={layers}
              toggleLayer={toggleLayer}
            />
          </Paper>

          <Paper sx={{ p: 2 }}>
            <ModelAnalysisIndicators
              available={available}
              layers={layers}
              toggleLayer={toggleLayer}
            />
          </Paper>
        </Grid>

        {/* график */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 1 }}>
            <TradingViewChart data={data} layers={layers} />
          </Paper>
        </Grid>

        {/* результаты */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, maxHeight: '82vh', overflow: 'auto' }}>
            <AnalysisSections analysis={analysis} />
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

