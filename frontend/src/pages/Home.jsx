// src/pages/Home.jsx

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

import TradingViewChart   from '../components/TradingViewChart';
import IndicatorsSidebar  from '../components/IndicatorsSidebar';
import CommentsPanel      from '../components/CommentsPanel';
import VolumePanel        from '../components/VolumePanel';
import OscillatorsPanel   from '../components/OscillatorsPanel';
import MACDPanel          from '../components/MACDPanel';
import InsightsPanel      from '../components/InsightsPanel';

export default function Home() {
  const [data, setData]                 = useState({ candles: [], volume: [] });
  const [analysis, setAnalysis]         = useState({});
  const [activeLayers, setActiveLayers] = useState([]);
  const [chartType, setChartType]       = useState('candles');
  const [resolution, setResolution]     = useState('1D');
  const [legendMeta, setLegendMeta]     = useState([]);

  // Загрузка данных и анализа
  useEffect(() => {
    async function fetchAll() {
      const respData = await axios.get('/api/market-data');
      const respAnal = await axios.get('/api/model-analysis');
      setData(respData.data);
      setAnalysis(respAnal.data);
      // Изначально включаем все базовые и modelAnalysis слои
      setActiveLayers([
        ...Object.keys(analysis ? analysis : {})
      ]);
    }
    fetchAll();
  }, []);

  // Колбек для Legend: обновляем легенду при регистрации серии
  const handleLegendMeta = useCallback(meta => {
    setLegendMeta(prev => {
      const without = prev.filter(item => item.key !== meta.key);
      return [...without, meta];
    });
  }, []);

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <IndicatorsSidebar
        activeLayers={activeLayers}
        setActiveLayers={setActiveLayers}
      />

      <div style={{ flex: 1, position: 'relative' }}>
        <TradingViewChart
          rawPriceData={data.candles}
          rawVolumeData={data.volume}
          analysis={analysis}
          activeLayers={activeLayers}
          chartType={chartType}
          resolution={resolution}
          onSeriesMetaChange={handleLegendMeta}
        />

        <div style={{ position: 'absolute', bottom: 0, width: '100%' }}>
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

        <CommentsPanel
          analysis={analysis}
          activeLayers={activeLayers}
        />

        <InsightsPanel
          analysis={analysis}
        />
      </div>
    </div>
  );
}
