// src/pages/Home.jsx

import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import { useSelector } from 'react-redux';
import { Box, Snackbar, Alert, Divider } from '@mui/material';
import { parseOhlc } from '../utils/chartUtils';

import IndicatorsSidebar from '../components/IndicatorsSidebar';
import AnalysisControls   from '../components/AnalysisControls';
import TradingViewChart   from '../components/TradingViewChart';
import CommentsPanel    from '../components/CommentsPanel';
import InsightsPanel    from '../components/InsightsPanel';
import VolumePanel      from '../components/VolumePanel';
import OscillatorsPanel from '../components/OscillatorsPanel';
import MACDPanel        from '../components/MACDPanel';
import {
  overlays,
  volume,
  momentum,
  volatility,
  macd,
  modelAnalysis,
  forecast,
} from '../data/indicatorGroups';

export default function Home() {
  const [data, setData]                 = useState({ candles: [], volume: [] });
  const [analysis, setAnalysis]         = useState({});
  const [activeLayers, setActiveLayers] = useState([]);
  const [symbol, setSymbol]             = useState('BTCUSDT');
  const [interval, setInterval]         = useState('4h');
  const [limit, setLimit]               = useState(144);
  const [chartType, setChartType]       = useState('candles');
  const [resolution, setResolution]     = useState('1D');
  const [legendMeta, setLegendMeta]     = useState([]);
  const [errorOpen, setErrorOpen]       = useState(false);
  const chartApiRef                     = useRef(null);

  const token = useSelector(state => state.auth.token);

  async function fetchAll(symbolParam, intervalParam, limitParam) {
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    const resp = await axios.post('/api/analyze', {
      symbol: symbolParam,
      interval: intervalParam,
      limit: limitParam,
    }, { headers });

    if (resp.data.invalid_chatgpt_response) {
      setErrorOpen(true);
    }

    const parsed = parseOhlc(resp.data.ohlc);
    const candles = parsed.map(({ time, open, high, low, close }) => ({
      time, open, high, low, close,
    }));
    const volumeData = parsed.map(d => ({
      time: d.time,
      value: Number(d.Volume),
      open: d.open,
      close: d.close,
    }));

    setData({ candles, volume: volumeData });
    setAnalysis(resp.data.analysis);
    setActiveLayers([
      ...overlays,
      ...volume,
      ...momentum,
      ...volatility,
      ...macd,
      ...modelAnalysis,
      ...forecast,
    ]);
  }

  useEffect(() => {
    fetchAll(symbol, interval, limit);
  }, []);

  // Заготовка функции скрытия/показа серии (надо реализовать в TradingViewChart через callback или context)
  const toggleSeriesVisibility = (key) => {
    setLegendMeta(prev =>
      prev.map(item =>
        item.key === key ? { ...item, visible: !item.visible } : item
      )
    );
    chartApiRef.current?.toggleSeries(key);
  };

  const handleLegendMeta = useCallback(metaItem => {
    setLegendMeta(prev => {
      const without = prev.filter(item => item.key !== metaItem.key);
      // Добавляем новое или обновлённое описание слоя, помечаем как видимое по умолчанию
      return [
        ...without,
        { ...metaItem, visible: true, onToggle: () => toggleSeriesVisibility(metaItem.key) },
      ];
    });
  }, [toggleSeriesVisibility]);

  const onAnalyze = ({ symbol, interval, limit }) => {
    fetchAll(symbol, interval, limit);
  };

  const onLoadTest = async () => {
    const resp = await axios.get('/api/testdata');
    const parsed = parseOhlc(resp.data.ohlc);
    const candles = parsed.map(({ time, open, high, low, close }) => ({
      time, open, high, low, close,
    }));
    const volumeData = parsed.map(d => ({
      time: d.time,
      value: Number(d.Volume),
      open: d.open,
      close: d.close,
    }));

    setData({ candles, volume: volumeData });
    setAnalysis(resp.data.analysis);
  };
  return (
    <>
    <Box display="flex" gap={2} height="100vh" p={1}>
      <Box sx={{ width: 240, flexShrink: 0 }}>
        <IndicatorsSidebar
          activeLayers={activeLayers}
          setActiveLayers={setActiveLayers}
        />
      </Box>

      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
        <Box sx={{ flex: 0 }}>
          {/* Добавляем панель селекторов и кнопок */}
          <AnalysisControls
            symbol={symbol}
            setSymbol={setSymbol}
            interval={interval}
            setInterval={setInterval}
            limit={limit}
            setLimit={setLimit}
            onAnalyze={onAnalyze}
            onLoadTest={onLoadTest}
          />
        </Box>
        <Box sx={{ flex: 1, position: 'relative', minHeight: 0 }}>
          <TradingViewChart
            ref={chartApiRef}
            rawPriceData={data.candles}
            rawVolumeData={data.volume}
            analysis={analysis}
            activeLayers={activeLayers}
            chartType={chartType}
            resolution={resolution}
            onSeriesMetaChange={handleLegendMeta}
            legendMeta={legendMeta}
          />
        </Box>
        <Box sx={{ flex: '0 0 auto', overflowY: 'auto', maxHeight: 250 }}>
          <VolumePanel
            volumeData={data.volume}
            obvData={analysis.OBV || []}
          />
          <OscillatorsPanel
            rsi={analysis.RSI || []}
            stochastic={{
              k: analysis.Stochastic_Oscillator?.map(i => ({ time: i.date, value: i.k })) || [],
              d: analysis.Stochastic_Oscillator?.map(i => ({ time: i.date, value: i.d })) || [],
            }}
            williams={analysis['Williams_%R']?.map(i => ({ time: i.date, value: i.value })) || []}
          />
          <MACDPanel
            macd={analysis.MACD || []}
            signal={analysis.MACD_signal || []}
            histogram={analysis.MACD_hist || []}
          />
        </Box>
      </Box>

      <Box sx={{ width: 300, flexShrink: 0 }}>
        <CommentsPanel
          analysis={analysis}
          activeLayers={activeLayers}
        />
        <Divider sx={{ my: 1 }} />
        <InsightsPanel analysis={analysis} />
      </Box>
    </Box>
    <Snackbar
      open={errorOpen}
      autoHideDuration={6000}
      onClose={() => setErrorOpen(false)}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
    >
      <Alert severity="warning" onClose={() => setErrorOpen(false)} sx={{ width: '100%' }}>
        Анализ не выполнен из-за некорректного ответа модели
      </Alert>
    </Snackbar>
    </>
  );
}
