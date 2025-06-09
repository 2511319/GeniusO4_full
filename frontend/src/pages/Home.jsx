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
import CommentsPanel           from '../CommentsPanel';
import VolumePanel            from '../VolumePanel';
import OscillatorsPanel       from '../OscillatorsPanel';
import MACDPanel              from '../MACDPanel';
import { parseOhlc, parsePatterns } from '../chartUtils';
import { validateAnalysis } from '../analysisValidator';
import { fetchAnalysis } from '../services/analysisLoader';
import IndicatorsSidebar from '../IndicatorsSidebar';

export default function Home() {
  const token = useSelector((s) => s.auth.token);

  const [symbol,  setSymbol]  = useState('BTCUSDT');
  const [interval,setInterval]= useState('4h');
  const [limit,   setLimit]   = useState(144);
  const [layers,  setLayers]  = useState(['RSI']);
  const [data,    setData]    = useState([]);
  const [analysis,setAnalysis]= useState(null);
  const [explanations, setExplanations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hideL,   setHideL]   = useState(false);
  const [hideR,   setHideR]   = useState(false);
  const [chartType, setChartType] = useState('candles');
  const [patterns, setPatterns] = useState([]);
  const [showSR, setShowSR] = useState(false);
  const [showTrends, setShowTrends] = useState(false);

  const toggleLayer = (name) =>
    setLayers((prev) =>
      prev.includes(name) ? prev.filter((l) => l !== name) : [...prev, name]);

  const loadTestData = async () => {
    try {
      setLoading(true);
      const analysisData = await fetchAnalysis();
      if (!analysisData) {
        alert('Нет сохранённых данных');
        return;
      }
      validateAnalysis(analysisData);
      setAnalysis(analysisData);
      setExplanations([]);
      setData([]);
      setPatterns(parsePatterns(analysisData.candlestick_patterns));
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
    validateAnalysis(json.analysis);
    setAnalysis(json.analysis);
    setExplanations(json.explanations || []);
    setData(parseOhlc(json.ohlc));
    setPatterns(parsePatterns(json.analysis?.candlestick_patterns));
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

          <IndicatorsSidebar
            layers={layers}
            toggleLayer={toggleLayer}
            showSR={showSR}
            setShowSR={setShowSR}
            showTrends={showTrends}
            setShowTrends={setShowTrends}
          />
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
          <Box sx={{ height: '100%', position: 'relative', display: 'flex', flexDirection: 'column' }}>
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
                <Box sx={{ flex: 1, position: 'relative' }}>
                  <TradingViewChart
                    data={data}
                    patterns={patterns}
                    layers={layers}
                    type={chartType}
                    showSR={showSR}
                    showTrends={showTrends}
                  />
                </Box>
                {layers.includes('Volume') && <VolumePanel data={data} />}
                {layers.some((l) => ['RSI', 'Stochastic_Oscillator', 'Williams_%R', 'OBV'].includes(l)) && (
                  <OscillatorsPanel data={data} layers={layers} />
                )}
                {layers.includes('MACD') && <MACDPanel data={data} />}
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
            <CommentsPanel analysis={analysis} explanations={explanations} layers={layers} />
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
