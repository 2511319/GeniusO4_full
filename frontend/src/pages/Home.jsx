// src/pages/Home.jsx

import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import { useSelector } from 'react-redux';

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

export default function Home({ sidebarOpen, commentsOpen, setSidebarOpen, setCommentsOpen }) {
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
  const fetchTimer                      = useRef(null);

  useEffect(() => {
    if (errorOpen) {
      const timer = setTimeout(() => setErrorOpen(false), 6000);
      return () => clearTimeout(timer);
    }
  }, [errorOpen]);

  const token = useSelector(state => state.auth.token);

  const fetchAll = useCallback(async (symbolParam, intervalParam, limitParam) => {
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
  }, [token]);

  const scheduleFetch = useCallback((sym, intv, lim) => {
    if (fetchTimer.current) clearTimeout(fetchTimer.current);
    fetchTimer.current = setTimeout(() => {
      fetchAll(sym, intv, lim);
    }, 300);
  }, [fetchAll]);

  useEffect(() => {
    fetchAll(symbol, interval, limit);
  }, []); // initial load

  const handleIntervalChange = useCallback(
    (val) => {
      setInterval(val);
      scheduleFetch(symbol, val, limit);
    },
    [symbol, limit, scheduleFetch]
  );

  const handleLimitChange = useCallback(
    (val) => {
      setLimit(val);
      scheduleFetch(symbol, interval, val);
    },
    [symbol, interval, scheduleFetch]
  );

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
    <div className="flex gap-2 h-screen p-2">
      {sidebarOpen && (
        <div className="w-[240px] flex-shrink-0">
          <IndicatorsSidebar
            activeLayers={activeLayers}
            setActiveLayers={setActiveLayers}
          />
        </div>
      )}

      <div className="flex flex-col flex-1 h-full">
        <div className="flex-none">
          {/* Добавляем панель селекторов и кнопок */}
          <AnalysisControls
            symbol={symbol}
            setSymbol={setSymbol}
            interval={interval}
            onIntervalChange={handleIntervalChange}
            limit={limit}
            onLimitChange={handleLimitChange}
            onAnalyze={onAnalyze}
            onLoadTest={onLoadTest}
          />
        </div>
        <div className="relative flex-1 min-h-0">
          <TradingViewChart
            ref={chartApiRef}
            rawPriceData={data.candles}
            rawVolumeData={data.volume}
            analysis={analysis}
            activeLayers={activeLayers}
            chartType={chartType}
            setChartType={setChartType}
            resolution={resolution}
            onSeriesMetaChange={handleLegendMeta}
            legendMeta={legendMeta}
            setSidebarOpen={setSidebarOpen}
            setCommentsOpen={setCommentsOpen}
          />
        </div>
        <div className="flex-none overflow-y-auto max-h-[250px]">
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
        </div>
      </div>

      {commentsOpen && (
        <div className="w-[300px] flex-shrink-0 z-10">
          <CommentsPanel
            analysis={analysis}
            activeLayers={activeLayers}
          />
          <hr className="my-1 border-gray-300" />
          <InsightsPanel analysis={analysis} />
        </div>
      )}
    </div>
    {errorOpen && (
      <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 transition-opacity duration-300">
        <div className="relative bg-yellow-100 border border-yellow-400 text-yellow-800 px-4 py-2 rounded shadow">
          <button
            className="absolute top-1 right-1 text-yellow-800"
            onClick={() => setErrorOpen(false)}
          >
            ✕
          </button>
          Анализ не выполнен из-за некорректного ответа модели
        </div>
      </div>
    )}
    </>
  );
}
