// src/components/TradingViewChart.jsx

import React, {
  useEffect, useRef, useMemo, useState, useCallback, useImperativeHandle,
} from 'react';
import PropTypes from 'prop-types';
import { createChart, CrosshairMode } from 'lightweight-charts';
import { Box } from '@mui/material';

import ChartControls from './ChartControls';
import Legend        from './Legend';

import { validateAnalysis } from '../data/analysisValidator';
import { computeHeikinAshi, computeRenko, parseToUnix } from '../utils/chartUtils';

const prettify = key =>
  key.split('_').map(w => w[0].toUpperCase() + w.slice(1)).join(' ');

const TradingViewChart = React.forwardRef(function TradingViewChart({
  rawPriceData,
  rawVolumeData,
  analysis,
  activeLayers,
  chartType,
  resolution,
  onSeriesMetaChange,
  legendMeta,
}, ref) {
  const containerRef = useRef(null);
  const chartRef     = useRef(null);
  const seriesStore  = useRef({});

  useImperativeHandle(ref, () => ({
    toggleSeries: (key) => {
      const s = seriesStore.current[key];
      if (!s || !s.applyOptions) return;
      const visible = s.options?.().visible !== false;
      s.applyOptions({ visible: !visible });
    },
  }));

  const [forecast] = useState(analysis.price_prediction?.virtual_candles || []);

  // 1. Валидация JSON
  useEffect(() => { if (analysis) validateAnalysis(analysis); }, [analysis]);

  // 2. Price data в зависимости от chartType
  const priceData = useMemo(() => {
    if (chartType === 'heikin') return computeHeikinAshi(rawPriceData);
    if (chartType === 'renko')  return computeRenko(rawPriceData, resolution);
    return rawPriceData;
  }, [rawPriceData, chartType, resolution]);

  const volumeData = useMemo(
    () => rawVolumeData.map(d => ({
      time: d.time,
      value: d.value,
      color: d.open > d.close ? '#e74c3c' : '#2ecc71',
    })),
    [rawVolumeData]
  );

  // 3. Инициализация chart и price
  useEffect(() => {
    if (!containerRef.current) return;
    chartRef.current = createChart(containerRef.current, {
      layout: { backgroundColor: '#fff', textColor: '#000' },
      crosshair: { mode: CrosshairMode.Normal },
      rightPriceScale: { scaleMargins: { top: 0.1, bottom: 0.15 } },
      timeScale: { timeVisible: true },
      width:  containerRef.current.clientWidth,
      height: containerRef.current.clientHeight,
    });
    const ps = chartRef.current.addCandlestickSeries();
    ps.setData(priceData);
    seriesStore.current.price = ps;

    const handleResize = () => {
      chartRef.current.resize(
        containerRef.current.clientWidth,
        containerRef.current.clientHeight
      );
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chartRef.current.remove();
    };
  }, []);

  useEffect(() => { seriesStore.current.price?.setData(priceData); }, [priceData]);

  // Обновление серии объёма при смене слоя или данных
  useEffect(() => {
    if (!chartRef.current) return;
    let vs = seriesStore.current.volume;
    const shouldShow = activeLayers.includes('Volume');
    if (shouldShow) {
      if (!vs) {
        vs = chartRef.current.addHistogramSeries({
          priceScaleId: '',
          scaleMargins: { top: 0.8, bottom: 0 },
          color: '#2ecc71',
        });
        seriesStore.current.volume = vs;
      }
      vs.setData(volumeData);
      vs.applyOptions({ visible: true });
    } else if (vs) {
      vs.applyOptions({ visible: false });
    }
    onSeriesMetaChange?.({ key: 'Volume', name: 'Volume', color: '#2ecc71', icon: '▉' });
  }, [activeLayers, volumeData]);

  // 4. Forecast-candles
  useEffect(() => {
    if (seriesStore.current.forecast) {
      chartRef.current.removeSeries(seriesStore.current.forecast);
      delete seriesStore.current.forecast;
    }
    if (forecast.length) {
      const fs = chartRef.current.addCandlestickSeries({
        upColor: 'rgba(0,150,0,0.4)', downColor: 'rgba(150,0,0,0.4)',
        borderVisible: true, priceFormat: { type: 'ohlc' }, lastValueVisible: false,
      });
      fs.setData(forecast);
      seriesStore.current.forecast = fs;
      onSeriesMetaChange?.({
        key: 'price_prediction',
        name: 'Forecast',
        color: 'rgba(0,150,0,0.4)',
        icon: '⧉',
      });
    }
  }, [forecast]);

  // 5. Технические overlay
  useEffect(() => {
    const ind = analysis;
    const register = (k,s,c,d,i) => {
      seriesStore.current[k] = s;
      onSeriesMetaChange?.({ key:k, name:prettify(k), color:c, dashed:d, icon:i });
    };

    // удалить старые
    Object.keys(seriesStore.current)
      .filter(k => /(MA_|VWAP|Bollinger|Moving_Average_Envelope|Parabolic_SAR|Ichimoku_|Volume|OBV|RSI|Stochastic_Oscillator|Williams_%R|ATR|MACD)/.test(k))
      .forEach(k => {
        chartRef.current.removeSeries(seriesStore.current[k]);
        delete seriesStore.current[k];
      });

    // MA
    [['MA_20','#2979ff'],['MA_50','#0288d1'],['MA_100','#0277bd'],['MA_200','#01579b']].forEach(([key,color])=>{
      if(activeLayers.includes(key)&&Array.isArray(ind[key])){
        const s=chartRef.current.addLineSeries({ color, lineWidth:1 });
        s.setData(ind[key].map(p=>({time:parseToUnix(p.date),value:p.value})));
        register(key,s,color,false,'─');
      }
    });

    // VWAP
    if(activeLayers.includes('VWAP')&&Array.isArray(ind.VWAP)){
      const s=chartRef.current.addLineSeries({ color:'#ff9800', lineWidth:1 });
      s.setData(ind.VWAP.map(p=>({time:parseToUnix(p.date),value:p.value}))); 
      register('VWAP',s,'#ff9800',false,'─');
    }

    // Bollinger Bands
    [['Bollinger_Middle','#9e9e9e',0],['Bollinger_Upper','#bdbdbd',2],['Bollinger_Lower','#bdbdbd',2]]
      .forEach(([key,color,style])=>{
        if(activeLayers.includes(key)&&Array.isArray(ind[key])){
          const s=chartRef.current.addLineSeries({ color, lineWidth:1, lineStyle:style });
          s.setData(ind[key].map(p=>({time:parseToUnix(p.date),value:p.value})));
          register(key,s,color,style!==0,'─');
        }
      });

    // Envelope
    ['Moving_Average_Envelope_Upper','Moving_Average_Envelope_Lower'].forEach(key=>{
      if(activeLayers.includes(key)&&Array.isArray(ind[key])){
        const color='#4caf50';
        const s=chartRef.current.addLineSeries({ color, lineWidth:1, lineStyle:2 });
        s.setData(ind[key].map(p=>({time:parseToUnix(p.date),value:p.value})));
        register(key,s,color,true,'─');
      }
    });

    // Parabolic SAR
    if(activeLayers.includes('Parabolic_SAR')&&Array.isArray(ind.Parabolic_SAR)){
      const s=chartRef.current.addLineSeries({ lineWidth:0 });
      s.setMarkers(ind.Parabolic_SAR.map(p=>({
        time:parseToUnix(p.date),
        position:p.value>priceData[priceData.length-1].low?'aboveBar':'belowBar',
        color:'#ffeb3b',
        shape:'circle'
      })));
      register('Parabolic_SAR',s,'#ffeb3b',false,'•');
    }

    // Ichimoku
    if(activeLayers.includes('Ichimoku_Conversion_Line')&&Array.isArray(ind.Ichimoku_Conversion_Line)){
      const s=chartRef.current.addLineSeries({ color:'#d32f2f',lineWidth:1 });
      s.setData(ind.Ichimoku_Conversion_Line.map(p=>({time:parseToUnix(p.date),value:p.value}))); 
      register('Ichimoku_Conversion_Line',s,'#d32f2f',false,'─');
    }
    if(activeLayers.includes('Ichimoku_Base_Line')&&Array.isArray(ind.Ichimoku_Base_Line)){
      const s=chartRef.current.addLineSeries({ color:'#1976d2',lineWidth:1 });
      s.setData(ind.Ichimoku_Base_Line.map(p=>({time:parseToUnix(p.date),value:p.value}))); 
      register('Ichimoku_Base_Line',s,'#1976d2',false,'─');
    }
    if(activeLayers.includes('Ichimoku_A')&&activeLayers.includes('Ichimoku_B')
       &&Array.isArray(ind.Ichimoku_A)&&Array.isArray(ind.Ichimoku_B)){
      const cloud=chartRef.current.addAreaSeries({
        topColor:'rgba(156,39,176,0.2)',
        bottomColor:'rgba(156,39,176,0.05)',
        lineColor:'rgba(156,39,176,0.6)'
      });
      cloud.setData(ind.Ichimoku_A.map(p=>({time:parseToUnix(p.date),value:p.value}))); 
      register('Ichimoku_Cloud',cloud,'rgba(156,39,176,0.6)',false,'▧');
    }
  },[analysis,activeLayers,priceData]);

  // 7. ModelAnalysis-слои
  const renderModelLayer = useCallback((layer)=>{
    const arr=analysis[layer];
    if(!activeLayers.includes(layer)||!Array.isArray(arr))return;
    const register=(k,s,c,d,i)=>{
      seriesStore.current[k]=s;
      onSeriesMetaChange?.({key:k,name:prettify(k),color:c,dashed:d,icon:i});
    };

    if(layer==='support_resistance_levels'){
      arr.forEach((it,i)=>{
        const s=chartRef.current.addLineSeries({color:it.type==='support'?'green':'red',lineWidth:1});
        s.setData([{time:parseToUnix(it.date),value:it.level},{time:priceData[priceData.length-1].time,value:it.level}]);
        register(`${layer}_${i}`,s,s.options().color,false,'─');
      });
      return;
    }
    if(layer==='trend_lines'){
      arr.forEach((it,i)=>{
        const s=chartRef.current.addLineSeries({color:it.type==='ascending'?'green':'red',lineWidth:2});
        s.setData([{time:parseToUnix(it.start_point.date),value:it.start_point.price},{time:parseToUnix(it.end_point.date),value:it.end_point.price}]);
        register(`${layer}_${i}`,s,s.options().color,false,'─');
      });
      return;
    }
    if(layer==='fibonacci_analysis'){
      arr.forEach((fib,i)=>{
        fib.levels.forEach((lvl,j)=>{
          const s=chartRef.current.addLineSeries({color:lvl.color,lineStyle:2,lineWidth:1});
          s.setData([{time:parseToUnix(fib.start_point.date),value:lvl.value},{time:parseToUnix(fib.end_point.date),value:lvl.value}]);
          register(`${layer}_${i}_${j}`,s,lvl.color,true,'─');
        });
      });
      return;
    }
    ['unfinished_zones','imbalances','fair_value_gaps','gap_analysis'].forEach(zKey=>{
      if(layer!==zKey)return;
      arr.forEach((z,i)=>{
        const s=chartRef.current.addAreaSeries({
          topColor:'rgba(0,123,255,0.2)',
          bottomColor:'rgba(0,123,255,0.05)',
          lineColor:'rgba(0,123,255,0.5)',lineWidth:1
        });
        if(z.start_point&&z.end_point){
          s.setData([{time:parseToUnix(z.start_point.date),value:z.start_point.price},{time:parseToUnix(z.end_point.date),value:z.end_point.price}]);
        } else if(z.date&&Array.isArray(z.price_range)){
          const [low,high]=z.price_range;
          s.setData([{time:parseToUnix(z.date),value:low},{time:parseToUnix(z.date),value:high}]);
          console.warn(`Missing coords for ${layer}[${i}], fallback used`);
        }
        register(`${layer}_${i}`,s,'rgba(0,123,255,0.5)',false,'▧');
      });
    });
    ['structural_edge','candlestick_patterns','divergence_analysis'].forEach(mKey=>{
      if(layer!==mKey)return;
      arr.forEach((it,i)=>{
        const s=chartRef.current.addLineSeries({lineWidth:0});
        s.setMarkers([{time:parseToUnix(it.date),position:'aboveBar',color:'#ff00ff',shape:'circle',text:it.type[0]||''}]);
        register(`${layer}_${i}`,s,'#ff00ff',false,'●');
      });
    });
  },[analysis,activeLayers,priceData]);

  useEffect(()=>{
    // удалить modelAnalysis серии
    Object.keys(seriesStore.current)
      .filter(k=>/^(support_resistance_levels|trend_lines|fibonacci_analysis|unfinished_zones|imbalances|fair_value_gaps|gap_analysis|structural_edge|candlestick_patterns|divergence_analysis)_/.test(k))
      .forEach(k=>{
        chartRef.current.removeSeries(seriesStore.current[k]);
        delete seriesStore.current[k];
      });
    [
      'support_resistance_levels','trend_lines','fibonacci_analysis',
      'unfinished_zones','imbalances','fair_value_gaps','gap_analysis',
      'structural_edge','candlestick_patterns','divergence_analysis',
    ].forEach(renderModelLayer);
  },[analysis,activeLayers,renderModelLayer]);

  return (
    <Box sx={{position:'relative',width:'100%',height:'100%'}}>
      <Box ref={containerRef} sx={{width:'100%',height:'100%'}}/>
      <ChartControls containerRef={containerRef} chartRef={chartRef} seriesStore={seriesStore}/>
      <Legend meta={legendMeta} />
    </Box>
  );
});

TradingViewChart.propTypes = {
  rawPriceData:      PropTypes.array.isRequired,
  rawVolumeData:     PropTypes.array.isRequired,
  analysis:          PropTypes.object.isRequired,
  activeLayers:      PropTypes.arrayOf(PropTypes.string).isRequired,
  chartType:         PropTypes.oneOf(['candles','heikin','renko']).isRequired,
  resolution:        PropTypes.string.isRequired,
  onSeriesMetaChange:PropTypes.func,
  legendMeta: PropTypes.array,
};

export default TradingViewChart;
