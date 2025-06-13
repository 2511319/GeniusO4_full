// src/data/analysisValidator.js

/**
 * Проверка обязательных полей в ответе модели.
 * Не бросает исключения, а выводит console.warn.
 */

const sectionRequirements = {
  primary_analysis: ['global_trend', 'local_trend', 'patterns', 'anomalies'],
  confidence_in_trading_decisions: ['level', 'reason'],

  // Технические индикаторы: проверяем только наличие секции
  MA_20: [], MA_50: [], MA_100: [], MA_200: [],
  VWAP: [],
  Bollinger_Middle: [], Bollinger_Upper: [], Bollinger_Lower: [],
  Moving_Average_Envelope_Upper: [], Moving_Average_Envelope_Lower: [],
  Parabolic_SAR: [],
  Ichimoku_Conversion_Line: [], Ichimoku_Base_Line: [], Ichimoku_A: [], Ichimoku_B: [],

  // Model Analysis
  support_resistance_levels: ['date', 'level', 'explanation'],
  trend_lines: ['start_point', 'end_point', 'explanation'],
  fibonacci_analysis: ['start_point', 'end_point', 'levels', 'explanation'],
  unfinished_zones: ['start_point', 'end_point', 'explanation'],
  imbalances: ['start_point', 'end_point', 'explanation'],
  fair_value_gaps: ['start_point', 'end_point', 'explanation'],
  gap_analysis: ['gaps'], // далее проверяем содержимое gaps

  structural_edge: ['date', 'price', 'explanation'],
  candlestick_patterns: ['date', 'type', 'explanation'],
  divergence_analysis: ['indicator', 'type', 'date', 'explanation'],

  // Прочие разделы
  pivot_points: ['daily', 'weekly', 'monthly'],
  indicators_analysis: [],
  volume_analysis: ['volume_trends', 'significant_volume_changes'],
  indicator_correlations: ['correlations', 'explanation'],
  psychological_levels: ['level', 'date', 'type', 'explanation'],
  extended_ichimoku_analysis: ['details'],
  volatility_by_intervals: ['intervals'],
  anomalous_candles: ['date', 'price', 'explanation'],

  // Forecast & Recommendations
  price_prediction: ['virtual_candles'],
  recommendations: ['recommendations'],

  // Risk & Feedback
  risk_management: ['rules'],
  feedback: ['note', 'model_configuration', 'missed_data', 'issues_encountered', 'suggestions'],
};

export function validateAnalysis(analysis) {
  Object.entries(sectionRequirements).forEach(([section, fields]) => {
    const data = analysis[section];
    if (data == null) {
      console.warn(`Missing section: ${section}`);
      return;
    }
    if (section === 'gap_analysis') {
      if (!Array.isArray(data.gaps)) {
        console.warn('gap_analysis.gaps should be an array');
      } else {
        data.gaps.forEach((gap, i) => {
          if (!gap.start_point || !gap.end_point) {
            console.warn(`gap_analysis.gaps[${i}] missing start_point/end_point`);
          }
          if (!gap.explanation) {
            console.warn(`gap_analysis.gaps[${i}] missing explanation`);
          }
        });
      }
      return;
    }
    if (Array.isArray(data)) {
      data.forEach((item, idx) => {
        fields.forEach(f => {
          if (!(f in item)) {
            console.warn(`${section}[${idx}] missing field: ${f}`);
          }
        });
      });
    } else if (typeof data === 'object') {
      fields.forEach(f => {
        if (!(f in data)) {
          console.warn(`${section} missing field: ${f}`);
        }
      });
    }
  });
}
