import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import {
  Box, Paper, TextField, Select, MenuItem, Button,
  Typography, Divider, FormGroup, FormControlLabel,
  Checkbox, IconButton, CircularProgress,
} from '@mui/material';
import ChevronLeftIcon  from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import { SplitPane } from '@rexxars/react-split-pane';

import TradingViewChart       from '../TradingViewChart';
import ChartControls          from '../ChartControls';
import AnalysisSections        from '../AnalysisSections';
import TechnicalIndicators     from '../TechnicalIndicators';
import AdvancedIndicators      from '../AdvancedIndicators';
import ModelAnalysisIndicators from '../ModelAnalysisIndicators';
import { parseOhlc } from '../chartUtils';

export default function Home() {
  const token = useSelector((s) => s.auth.token);

  const [symbol,  setSymbol]  = useState('BTCUSDT');
  const [interval,setInterval]= useState('4h');
  const [limit,   setLimit]   = useState(144);
  const [layers,  setLayers]  = useState(['RSI']);
  const [data,    setData]    = useState([]);
  const [analysis,setAnalysis]= useState(null);
  const [loading, setLoading] = useState(false);
  const [hideL,   setHideL]   = useState(false);
  const [hideR,   setHideR]   = useState(false);
  const [chartType, setChartType] = useState('candles');
  const [showSR, setShowSR] = useState(false);
  const [showTrends, setShowTrends] = useState(false);

  const toggleLayer = (name) =>
    setLayers((prev) =>
      prev.includes(name) ? prev.filter((l) => l !== name) : [...prev, name]);

  const loadTestData = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/testdata');
      if (!res.ok) {
        alert('Нет сохранённых данных');
        setLoading(false);
        return;
      }
      const json = await res.json();
      setAnalysis(json.analysis || null);
      setData(parseOhlc(json.ohlc));
    } catch (err) {
      console.error(err);
      alert('Ошибка чтения тестовых данных');
    } finally {
      setLoading(false);
    }
  };

  const loadData = async () => {
    setLoading(true);
    const body = { symbol, interval, limit, indicators: layers };
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers.Authorization = `Bearer ${token}`;
    const res  = await fetch('/api/analyze', { method:'POST', headers, body:JSON.stringify(body) });
    const json = await res.json();
    setAnalysis(json.analysis);
    setData(parseOhlc(json.ohlc));
    setLoading(false);
  };

  /* ───────────────────────────── helpers */
  const leftPane = hideL ? 0 : 310;
  const rightPane= hideR ? 0 : 360;

  /* ───────────────────────────── UI */
  return (
    <Box sx={{ height: 'calc(100vh - 64px)', width: '100%' }}>
      <SplitPane
        split="vertical"
        minSize={hideL ? 0 : 220}
        size={leftPane}
        onChange={(size) => size < 80 && setHideL(true)}
      >
        {/* ───────────── левая колонка ───────────── */}
        <Paper
          square
          sx={{
            display: hideL ? 'none' : 'flex',
            flexDirection: 'column',
            height: '100%',
            p: 1,
            overflow: 'auto',
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <IconButton size="small" onClick={() => setHideL(true)}>
              <ChevronLeftIcon fontSize="inherit" />
            </IconButton>
          </Box>

          <Typography variant="h6" gutterBottom>Параметры запроса</Typography>
          <TextField
            fullWidth label="Тикер" sx={{ mb: 2 }}
            value={symbol} onChange={(e) => setSymbol(e.target.value)}
          />
          <TextField
            fullWidth type="number" label="Количество свечей" sx={{ mb: 2 }}
            value={limit} onChange={(e) => setLimit(+e.target.value)}
          />
          <Select
            fullWidth value={interval} label="Таймфрейм" sx={{ mb: 2 }}
            onChange={(e) => setInterval(e.target.value)}
          >
            {['1m','5m','15m','1h','4h','1d'].map((tf) => (
              <MenuItem key={tf} value={tf}>{tf}</MenuItem>
            ))}
          </Select>

          <Button variant="contained" fullWidth onClick={loadData}>
            Запустить анализ
          </Button>
          <Button variant="outlined" fullWidth sx={{ mt: 1 }} onClick={loadTestData}>
            Test
          </Button>

          <Divider sx={{ my: 2 }} />

          <Typography variant="subtitle1">Индикаторы графика</Typography>
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
            <FormControlLabel
              control={
                <Checkbox
                  checked={showSR}
                  onChange={(e) => setShowSR(e.target.checked)}
                />
              }
              label="Algo-SRlevel"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={showTrends}
                  onChange={(e) => setShowTrends(e.target.checked)}
                />
              }
              label="Trend lines"
            />
          </FormGroup>

          <TechnicalIndicators layers={layers} toggleLayer={toggleLayer} />
          <AdvancedIndicators layers={layers} toggleLayer={toggleLayer} />
          <ModelAnalysisIndicators layers={layers} toggleLayer={toggleLayer} />
        </Paper>

        {/* ───────────── центральный + правый блок ───────────── */}
        <SplitPane
          split="vertical"
          primary="second"
          minSize={hideR ? 0 : 260}
          size={rightPane}
          onChange={(size) => size < 80 && setHideR(true)}
        >
          {/* ───────────── график ───────────── */}
          <Box sx={{ height: '100%', position: 'relative' }}>
            {loading && (
              <Box
                sx={{
                  position: 'absolute',
                  inset: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 10,
                }}
              >
                <CircularProgress />
              </Box>
            )}
            {!loading && (
              <>
                <ChartControls type={chartType} onChange={setChartType} />
                <TradingViewChart
                  data={data}
                  layers={layers}
                  type={chartType}
                  showSR={showSR}
                  showTrends={showTrends}
                />
              </>
            )}
          </Box>

          {/* ───────────── правая колонка ───────────── */}
          <Paper
            square
            sx={{
              display: hideR ? 'none' : 'flex',
              flexDirection: 'column',
              height: '100%',
              overflow: 'auto',
              p: 1,
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <IconButton size="small" onClick={() => setHideR(true)}>
                <ChevronRightIcon fontSize="inherit" />
              </IconButton>
            </Box>
            <AnalysisSections analysis={analysis} />
          </Paper>
        </SplitPane>
      </SplitPane>

      {/* ───────────── кнопки вернуть панели ───────────── */}
      {hideL && (
        <IconButton
          size="small"
          sx={{
            position: 'absolute', top: 8, left: 8, zIndex: 20,
            backgroundColor: 'background.paper',
          }}
          onClick={() => setHideL(false)}
        >
          <ChevronRightIcon fontSize="inherit" />
        </IconButton>
      )}
      {hideR && (
        <IconButton
          size="small"
          sx={{
            position: 'absolute', top: 8, right: 8, zIndex: 20,
            backgroundColor: 'background.paper',
          }}
          onClick={() => setHideR(false)}
        >
          <ChevronLeftIcon fontSize="inherit" />
        </IconButton>
      )}
    </Box>
  );
}
