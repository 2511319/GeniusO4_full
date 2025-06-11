export const overlays = [
  'MA_20',
  'MA_50',
  'MA_100',
  'MA_200',
  'ADX',
  'Parabolic_SAR',
  'Ichimoku_Cloud'
];

export const volume = ['Volume', 'OBV'];

export const momentum = ['RSI', 'Stochastic_Oscillator', 'Williams_%R'];

export const volatility = ['ATR'];

export const macd = ['MACD'];

export const modelAnalysis = [
  'support_resistance_levels',
  'trend_lines',
  'unfinished_zones',
  'imbalances',
  'fibonacci_analysis',
  'elliott_wave_analysis',
  'structural_edge',
  'candlestick_patterns',
  'divergence_analysis',
  'fair_value_gaps',
  'gap_analysis',
  'psychological_levels',
  'anomalous_candles'
];

export const forecast = ['price_prediction', 'recommendations'];

export const indicatorColumnMap = {
  MACD: ['MACD', 'MACD_signal', 'MACD_hist'],
  Bollinger_Bands: ['Bollinger_Middle', 'Bollinger_Upper', 'Bollinger_Lower'],
  Ichimoku_Cloud: [
    'Ichimoku_A',
    'Ichimoku_B',
    'Ichimoku_Base_Line',
    'Ichimoku_Conversion_Line'
  ],
  Moving_Average_Envelopes: [
    'Moving_Average_Envelope_Upper',
    'Moving_Average_Envelope_Lower'
  ]
};
