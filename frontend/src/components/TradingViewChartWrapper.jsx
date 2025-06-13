import React from 'react';
import TradingViewChart from './TradingViewChart';

export default function ChartWrapper({ data = [], layers = [], forecast = [], analysis = {}, ...rest }) {
  const price = data;
  const volume = data.map(d => ({ time: d.time, value: d.value || d.volume || 0, open: d.open, close: d.close }));
  const merged = { ...analysis, price_prediction: { virtual_candles: forecast } };
  return (
    <TradingViewChart
      rawPriceData={price}
      rawVolumeData={volume}
      analysis={merged}
      activeLayers={layers}
      chartType="candles"
      resolution="1D"
      {...rest}
    />
  );
}
