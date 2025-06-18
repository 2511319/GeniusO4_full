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
    <Container maxWidth={false} sx={{ mt: 1, px: 1 }}>
      <Grid container spacing={1}>
        {/* левая панель */}
        <Grid item xs={12} lg={2.5}>
          <Accordion defaultExpanded sx={{ mb: 1 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ py: 0.5 }}>
              <Typography variant="subtitle1" fontWeight="bold">Параметры запроса</Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ py: 1 }}>

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
            <Button variant="outlined" fullWidth sx={{ mt: 1 }} onClick={loadTestData}>
              Test
            </Button>
            </AccordionDetails>
          </Accordion>

          <Accordion defaultExpanded sx={{ mb: 2 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}> 
              <Typography variant="subtitle1">Индикаторы графика</Typography>
            </AccordionSummary>
            <AccordionDetails>
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

          <Accordion defaultExpanded sx={{ mb: 2 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}> 
              <Typography variant="subtitle1">Технические</Typography>
            </AccordionSummary>
            <AccordionDetails>
            <TechnicalIndicators
              available={available}
              layers={layers}
              toggleLayer={toggleLayer}
            />
            </AccordionDetails>
          </Accordion>

          <Accordion defaultExpanded sx={{ mb: 2 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}> 
              <Typography variant="subtitle1">Продвинутые</Typography>
            </AccordionSummary>
            <AccordionDetails>
            <AdvancedIndicators
              available={available}
              layers={layers}
              toggleLayer={toggleLayer}
            />
            </AccordionDetails>
          </Accordion>

          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}> 
              <Typography variant="subtitle1">Модельный анализ</Typography>
            </AccordionSummary>
            <AccordionDetails>
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
          <Paper sx={{ p: 1.5, maxHeight: '82vh', overflow: 'auto' }}>
            <AnalysisSections analysis={analysis} activeLayers={layers} />
          </Paper>
        </Grid>
      </Grid>

      {/* Блок прогнозов и рекомендаций внизу */}
      {analysis && (analysis.price_prediction || analysis.recommendations) && (
        <Grid container spacing={2} sx={{ mt: 2 }}>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h5" gutterBottom color="primary">
                📈 Прогнозы и торговые рекомендации
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={3}>
                {analysis.price_prediction && (
                  <Grid item xs={12} md={6}>
                    <Box sx={{
                      p: 2,
                      bgcolor: 'background.paper',
                      borderRadius: 2,
                      border: '1px solid',
                      borderColor: 'primary.light'
                    }}>
                      <Typography variant="h6" gutterBottom color="primary">
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
                      p: 2,
                      bgcolor: 'background.paper',
                      borderRadius: 2,
                      border: '1px solid',
                      borderColor: 'success.light'
                    }}>
                      <Typography variant="h6" gutterBottom color="success.main">
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

