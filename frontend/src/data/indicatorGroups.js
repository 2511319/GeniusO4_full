// src/data/indicatorGroups.js

/**
 * Категории индикаторов для боковой панели.
 * Порядок обязателен: Overlays → Volume → Momentum → Volatility → MACD → Model Analysis → Forecast
 */

export const overlays = [
  'MA_20',
  'MA_50',
  'MA_100',
  'MA_200',
  'VWAP',
  'Bollinger_Middle',
  'Bollinger_Upper',
  'Bollinger_Lower',
  'Moving_Average_Envelope_Upper',
  'Moving_Average_Envelope_Lower',
  'Parabolic_SAR',
  'Ichimoku_Conversion_Line',
  'Ichimoku_Base_Line',
  'Ichimoku_A',
  'Ichimoku_B',
];

export const volume = [
  'Volume',
  'OBV',
];

export const momentum = [
  'RSI',
  'Stochastic_Oscillator',
  'Williams_%R',
];

export const volatility = [
  'ATR',
];

export const macd = [
  'MACD',
  'MACD_signal',
  'MACD_hist',
];

export const modelAnalysis = [
  'support_resistance_levels',
  'trend_lines',
  'fibonacci_analysis',
  'unfinished_zones',
  'imbalances',
  'fair_value_gaps',
  'gap_analysis',
  'structural_edge',
  'candlestick_patterns',
  'divergence_analysis',
];

export const forecast = [
  'price_prediction',
  'recommendations',
];

/**
 * Экспорт всех групп для удобного импорта
 */
export default {
  overlays,
  volume,
  momentum,
  volatility,
  macd,
  modelAnalysis,
  forecast,
};
