import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import {
  Container, Grid, Paper, Box,
  TextField, Select, MenuItem, Button, Typography,
  Divider, FormGroup, FormControlLabel, Checkbox,
  Accordion, AccordionSummary, AccordionDetails
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

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
  const [loading, setLoading] = useState(false);

  const toggleLayer = (name) =>
    setLayers((prev) =>
      prev.includes(name) ? prev.filter((l) => l !== name) : [...prev, name]);

  const loadTestData = async () => {
    try {
      const res = await fetch('/api/testdata');
      if (!res.ok) {
        alert('Нет сохранённых данных');
        return;
      }
      const json = await res.json();
      setAnalysis(json.analysis);
      setData(json.ohlc || []);
      setAvailable(json.indicators || []);
    } catch (err) {
      console.error(err);
      alert('Ошибка чтения тестовых данных');
    }
  };

  const loadData = async () => {
    try {
      setLoading(true);
      console.log('Запуск анализа...', { symbol, interval, limit, layers });

      const body = { symbol, interval, limit, indicators: layers };
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers.Authorization = `Bearer ${token}`;

      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers,
        body: JSON.stringify(body),
      });

      console.log('Ответ получен:', res.status, res.statusText);

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const json = await res.json();
      console.log('Данные анализа:', json);

      setAnalysis(json.analysis);
      setData(json.ohlc || []);
      setAvailable(json.indicators || []);

      console.log('Состояние обновлено');
    } catch (error) {
      console.error('Ошибка при загрузке данных:', error);
      alert('Ошибка при выполнении анализа: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth={false} sx={{ mt: 1, px: 1 }}>
      <Grid container spacing={1}>
        {/* левая панель */}
        <Grid item xs={12} lg={2.5}>
          <Accordion defaultExpanded sx={{ mb: 0.8 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ py: 0.3 }}>
              <Typography variant="subtitle1" fontWeight="bold" sx={{ fontSize: '0.9rem' }}>Параметры запроса</Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ py: 0.8 }}>

            <TextField
              fullWidth label="Тикер"
              value={symbol} onChange={(e) => setSymbol(e.target.value)}
              sx={{ mb: 1.5 }}
              size="small"
            />

            <TextField
              fullWidth type="number" label="Количество свечей"
              value={limit} onChange={(e) => setLimit(+e.target.value)}
              sx={{ mb: 1.5 }}
              size="small"
            />

            <Select
              fullWidth value={interval} label="Таймфрейм"
              onChange={(e) => setInterval(e.target.value)}
              sx={{ mb: 1.5 }}
              size="small"
            >
              {['1m','5m','15m','1h','4h','1d'].map((tf) => (
                <MenuItem key={tf} value={tf}>{tf}</MenuItem>
              ))}
            </Select>

            <Button
              variant="contained"
              fullWidth
              onClick={loadData}
              disabled={loading}
            >
              {loading ? 'Анализ выполняется...' : 'Запустить анализ'}
            </Button>
            <Button variant="outlined" fullWidth sx={{ mt: 1 }} onClick={loadTestData}>
              Test (файл)
            </Button>
            <Button
              variant="outlined"
              fullWidth
              sx={{ mt: 1 }}
              onClick={async () => {
                try {
                  setLoading(true);
                  const body = { symbol, interval, limit, indicators: layers };
                  const res = await fetch('/api/analyze-test', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body),
                  });
                  const json = await res.json();
                  setAnalysis(json.analysis);
                  setData(json.ohlc || []);
                  setAvailable(json.indicators || []);
                } catch (error) {
                  console.error('Ошибка тестового анализа:', error);
                  alert('Ошибка: ' + error.message);
                } finally {
                  setLoading(false);
                }
              }}
              disabled={loading}
            >
              Test (API)
            </Button>
            </AccordionDetails>
          </Accordion>

          <Accordion defaultExpanded sx={{ mb: 0.8 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ py: 0.3 }}>
              <Typography variant="subtitle1" sx={{ fontSize: '0.9rem' }}>Индикаторы графика</Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ py: 0.8 }}>
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
            </AccordionDetails>
          </Accordion>

          <Accordion defaultExpanded sx={{ mb: 0.8 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ py: 0.3 }}>
              <Typography variant="subtitle1" sx={{ fontSize: '0.9rem' }}>Технические</Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ py: 0.8 }}>
            <TechnicalIndicators
              available={available}
              layers={layers}
              toggleLayer={toggleLayer}
            />
            </AccordionDetails>
          </Accordion>

          <Accordion defaultExpanded sx={{ mb: 0.8 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ py: 0.3 }}>
              <Typography variant="subtitle1" sx={{ fontSize: '0.9rem' }}>Продвинутые</Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ py: 0.8 }}>
            <AdvancedIndicators
              available={available}
              layers={layers}
              toggleLayer={toggleLayer}
            />
            </AccordionDetails>
          </Accordion>

          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ py: 0.3 }}>
              <Typography variant="subtitle1" sx={{ fontSize: '0.9rem' }}>Модельный анализ</Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ py: 0.8 }}>
            <ModelAnalysisIndicators
              available={available}
              layers={layers}
              toggleLayer={toggleLayer}
            />
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* график */}
        <Grid item xs={12} lg={7}>
          <Paper sx={{ p: 0.5, height: 'fit-content' }}>
            <TradingViewChart data={data} layers={layers} analysis={analysis} />
          </Paper>
        </Grid>

        {/* результаты */}
        <Grid item xs={12} lg={2.5}>
          <Paper sx={{ p: 1, maxHeight: '82vh', overflow: 'auto' }}>
            <AnalysisSections analysis={analysis} activeLayers={layers} />
          </Paper>
        </Grid>
      </Grid>

      {/* Блок прогнозов и рекомендаций внизу */}
      {analysis && (analysis.price_prediction || analysis.recommendations) && (
        <Grid container spacing={1.5} sx={{ mt: 1.5 }}>
          <Grid item xs={12}>
            <Paper sx={{ p: 1.5 }}>
              <Typography variant="h6" gutterBottom color="primary" sx={{ fontSize: '1.1rem' }}>
                📈 Прогнозы и торговые рекомендации
              </Typography>
              <Divider sx={{ mb: 1.5 }} />
              <Grid container spacing={2}>
                {analysis.price_prediction && (
                  <Grid item xs={12} md={6}>
                    <Box sx={{
                      p: 1.5,
                      bgcolor: 'background.paper',
                      borderRadius: 2,
                      border: '1px solid',
                      borderColor: 'primary.light'
                    }}>
                      <Typography variant="subtitle1" gutterBottom color="primary" sx={{ fontSize: '1rem' }}>
                        🎯 Прогноз цены
                      </Typography>
                      <AnalysisSections
                        analysis={{ price_prediction: analysis.price_prediction }}
                        activeLayers={['price_prediction']}
                      />
                    </Box>
                  </Grid>
                )}
                {analysis.recommendations && (
                  <Grid item xs={12} md={6}>
                    <Box sx={{
                      p: 1.5,
                      bgcolor: 'background.paper',
                      borderRadius: 2,
                      border: '1px solid',
                      borderColor: 'success.light'
                    }}>
                      <Typography variant="subtitle1" gutterBottom color="success.main" sx={{ fontSize: '1rem' }}>
                        💡 Торговые рекомендации
                      </Typography>
                      <AnalysisSections
                        analysis={{ recommendations: analysis.recommendations }}
                        activeLayers={['recommendations']}
                      />
                    </Box>
                  </Grid>
                )}
              </Grid>
            </Paper>
          </Grid>
        </Grid>
      )}
    </Container>
  );
}

