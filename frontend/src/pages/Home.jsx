// src/pages/Home.jsx

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

import IndicatorsSidebar from '../components/IndicatorsSidebar';
import AnalysisControls   from '../components/AnalysisControls';
import TradingViewChart   from '../components/TradingViewChart';
import CommentsPanel    from '../components/CommentsPanel';
import InsightsPanel    from '../components/InsightsPanel';
import VolumePanel      from '../components/VolumePanel';
import OscillatorsPanel from '../components/OscillatorsPanel';
import MACDPanel        from '../components/MACDPanel';
import Legend           from '../components/Legend';  // ← добавлен импорт
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

  async function fetchAll(symbolParam, intervalParam, limitParam) {
    const respData = await axios.get('/api/market-data');
    const respAnal = await axios.get('/api/model-analysis', {
      params: { symbol: symbolParam, interval: intervalParam, limit: limitParam }
    });
    setData(respData.data);
    setAnalysis(respAnal.data);
    setActiveLayers(Object.keys(respAnal.data));
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

  // Заготовка функции скрытия/показа серии (надо реализовать в TradingViewChart через callback или context)
  const toggleSeriesVisibility = (key) => {
    setLegendMeta(prev =>
      prev.map(item =>
        item.key === key ? { ...item, visible: !item.visible } : item
      )
    );
    // TODO: вызвать внутри ChartControls или TradingViewChart логику show/hide для seriesStore.current[key]
  };

  const onAnalyze = ({ symbol, interval, limit }) => {
    fetchAll(symbol, interval, limit);
  };

  const onLoadTest = async () => {
    const resp = await axios.get('/api/dev_logs/latest');
    setAnalysis(resp.data);
  };
  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <IndicatorsSidebar
        activeLayers={activeLayers}
        setActiveLayers={setActiveLayers}
      />

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
        <div style={{ flex: 0 }}>
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
        </div>
        <div style={{ flex: 1, position: 'relative', minHeight: 0 }}>
          <TradingViewChart
            rawPriceData={data.candles}
            rawVolumeData={data.volume}
            analysis={analysis}
            activeLayers={activeLayers}
            chartType={chartType}
            resolution={resolution}
            onSeriesMetaChange={handleLegendMeta}
            legendMeta={legendMeta}
          />

          <CommentsPanel
            analysis={analysis}
            activeLayers={activeLayers}
          />

          <InsightsPanel analysis={analysis} />
        </div>
        <div style={{ flex: 0 }}>
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
    </div>
  );
}
