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
          <Accordion defaultExpanded sx={{
            mb: 0.8,
            bgcolor: 'rgba(33, 150, 243, 0.08)',
            border: '1px solid rgba(33, 150, 243, 0.2)',
            '&:before': { display: 'none' }
          }}>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon sx={{ color: '#90caf9' }} />}
              sx={{
                py: 0.3,
                minHeight: 32,
                bgcolor: 'rgba(33, 150, 243, 0.15)'
              }}
            >
              <Typography variant="subtitle1" sx={{
                fontWeight: 'bold',
                color: '#e3f2fd',
                fontSize: '0.9rem'
              }}>
                ⚙️ Параметры запроса
              </Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ py: 0.8, px: 1.5 }}>

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

          <Accordion defaultExpanded sx={{
            mb: 0.8,
            bgcolor: 'rgba(76, 175, 80, 0.08)',
            border: '1px solid rgba(76, 175, 80, 0.2)',
            '&:before': { display: 'none' }
          }}>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon sx={{ color: '#a5d6a7' }} />}
              sx={{
                py: 0.3,
                minHeight: 32,
                bgcolor: 'rgba(76, 175, 80, 0.15)'
              }}
            >
              <Typography variant="subtitle1" sx={{
                fontWeight: 'bold',
                color: '#c8e6c9',
                fontSize: '0.9rem'
              }}>
                📊 Индикаторы графика
              </Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ py: 0.8, px: 1.5 }}>
              <FormGroup sx={{ gap: 0.2 }}>
              {['RSI','MACD','OBV','ATR','VWAP'].map((ind) => (
                <FormControlLabel
                  key={ind}
                  control={
                    <Checkbox
                      checked={layers.includes(ind)}
                      onChange={() => toggleLayer(ind)}
                      sx={{
                        py: 0.2,
                        '& .MuiSvgIcon-root': { color: '#a5d6a7' }
                      }}
                    />
                  }
                  label={
                    <Typography sx={{
                      fontSize: '0.85rem',
                      color: '#e8f5e8',
                      fontWeight: layers.includes(ind) ? 600 : 400
                    }}>
                      {ind}
                    </Typography>
                  }
                  sx={{ my: 0.1 }}
                />
              ))}
              </FormGroup>
            </AccordionDetails>
          </Accordion>

          <Accordion defaultExpanded sx={{
            mb: 0.8,
            bgcolor: 'rgba(255, 152, 0, 0.08)',
            border: '1px solid rgba(255, 152, 0, 0.2)',
            '&:before': { display: 'none' }
          }}>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon sx={{ color: '#ffcc80' }} />}
              sx={{
                py: 0.3,
                minHeight: 32,
                bgcolor: 'rgba(255, 152, 0, 0.15)'
              }}
            >
              <Typography variant="subtitle1" sx={{
                fontWeight: 'bold',
                color: '#ffe0b2',
                fontSize: '0.9rem'
              }}>
                🔧 Технические
              </Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ py: 0.8, px: 1.5 }}>
            <TechnicalIndicators
              available={available}
              layers={layers}
              toggleLayer={toggleLayer}
            />
            </AccordionDetails>
          </Accordion>

          <Accordion defaultExpanded sx={{
            mb: 0.8,
            bgcolor: 'rgba(156, 39, 176, 0.08)',
            border: '1px solid rgba(156, 39, 176, 0.2)',
            '&:before': { display: 'none' }
          }}>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon sx={{ color: '#ce93d8' }} />}
              sx={{
                py: 0.3,
                minHeight: 32,
                bgcolor: 'rgba(156, 39, 176, 0.15)'
              }}
            >
              <Typography variant="subtitle1" sx={{
                fontWeight: 'bold',
                color: '#e1bee7',
                fontSize: '0.9rem'
              }}>
                🚀 Продвинутые
              </Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ py: 0.8, px: 1.5 }}>
            <AdvancedIndicators
              available={available}
              layers={layers}
              toggleLayer={toggleLayer}
            />
            </AccordionDetails>
          </Accordion>

          <Accordion defaultExpanded sx={{
            bgcolor: 'rgba(244, 67, 54, 0.08)',
            border: '1px solid rgba(244, 67, 54, 0.2)',
            '&:before': { display: 'none' }
          }}>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon sx={{ color: '#ef9a9a' }} />}
              sx={{
                py: 0.3,
                minHeight: 32,
                bgcolor: 'rgba(244, 67, 54, 0.15)'
              }}
            >
              <Typography variant="subtitle1" sx={{
                fontWeight: 'bold',
                color: '#ffcdd2',
                fontSize: '0.9rem'
              }}>
                🤖 Модельный анализ
              </Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ py: 0.8, px: 1.5 }}>
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
          <Paper sx={{
            p: 1.5,
            maxHeight: '82vh',
            overflow: 'auto',
            bgcolor: 'rgba(0, 0, 0, 0.4)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: 2,
            '&::-webkit-scrollbar': {
              width: '8px',
            },
            '&::-webkit-scrollbar-track': {
              background: 'rgba(255, 255, 255, 0.1)',
              borderRadius: '4px',
            },
            '&::-webkit-scrollbar-thumb': {
              background: 'rgba(33, 150, 243, 0.6)',
              borderRadius: '4px',
            },
            '&::-webkit-scrollbar-thumb:hover': {
              background: 'rgba(33, 150, 243, 0.8)',
            }
          }}>
            <Box sx={{
              mb: 1.5,
              p: 1,
              bgcolor: 'rgba(33, 150, 243, 0.15)',
              borderRadius: 1,
              border: '1px solid rgba(33, 150, 243, 0.3)',
              textAlign: 'center'
            }}>
              <Typography variant="h6" sx={{
                color: '#e3f2fd',
                fontWeight: 'bold',
                fontSize: '1rem'
              }}>
                📋 Результаты анализа
              </Typography>
            </Box>
            <AnalysisSections analysis={analysis} activeLayers={layers} />
          </Paper>
        </Grid>
      </Grid>

      {/* Блок прогнозов и рекомендаций внизу */}
      {analysis && (analysis.price_prediction || analysis.recommendations) && (
        <Grid container spacing={2} sx={{ mt: 2 }}>
          <Grid item xs={12}>
            <Paper sx={{
              p: 3,
              bgcolor: 'rgba(33, 150, 243, 0.08)',
              border: '2px solid rgba(33, 150, 243, 0.3)',
              borderRadius: 2
            }}>
              <Typography variant="h5" gutterBottom sx={{
                color: '#e3f2fd',
                fontWeight: 'bold',
                textAlign: 'center',
                mb: 2
              }}>
                📈 Прогнозы и торговые рекомендации
              </Typography>
              <Divider sx={{
                mb: 3,
                borderColor: 'rgba(33, 150, 243, 0.3)',
                borderWidth: 1
              }} />
              <Grid container spacing={3}>
                {analysis.price_prediction && (
                  <Grid item xs={12} md={6}>
                    <Box sx={{
                      p: 2.5,
                      bgcolor: 'rgba(76, 175, 80, 0.1)',
                      borderRadius: 2,
                      border: '2px solid rgba(76, 175, 80, 0.4)',
                      boxShadow: '0 4px 12px rgba(76, 175, 80, 0.2)'
                    }}>
                      <Typography variant="h6" gutterBottom sx={{
                        color: '#c8e6c9',
                        fontWeight: 'bold',
                        textAlign: 'center',
                        mb: 2
                      }}>
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
                      p: 2.5,
                      bgcolor: 'rgba(255, 152, 0, 0.1)',
                      borderRadius: 2,
                      border: '2px solid rgba(255, 152, 0, 0.4)',
                      boxShadow: '0 4px 12px rgba(255, 152, 0, 0.2)'
                    }}>
                      <Typography variant="h6" gutterBottom sx={{
                        color: '#ffe0b2',
                        fontWeight: 'bold',
                        textAlign: 'center',
                        mb: 2
                      }}>
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

