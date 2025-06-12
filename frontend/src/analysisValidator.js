// src/data/analysisValidator.js

/**
 * Проверяет структуру JSON-ответа от модели.
 * Для каждого раздела из списка sectionRequirements убеждается,
 * что присутствуют все необходимые поля.
 * В случае отсутствия — выводит console.warn, но не бросает ошибку.
 */

const sectionRequirements = {
  // Primary analysis
  primary_analysis: ['global_trend', 'local_trend', 'patterns', 'anomalies'],

  // Confidence
  confidence_in_trading_decisions: ['level', 'reason'],

  // Model Analysis layers
  support_resistance_levels: ['date', 'level', 'explanation'],
  trend_lines: ['start_point', 'end_point', 'explanation'],
  fibonacci_analysis: ['start_point', 'end_point', 'levels', 'explanation'],
  unfinished_zones: ['start_point', 'end_point', 'explanation'],
  imbalances: ['start_point', 'end_point', 'explanation'],
  fair_value_gaps: ['start_point', 'end_point', 'explanation'],
  gap_analysis: ['gaps'],  // специальная обработка ниже
  structural_edge: ['date', 'price', 'explanation'],
  candlestick_patterns: ['date', 'type', 'explanation'],
  divergence_analysis: ['indicator', 'type', 'date', 'explanation'],

  // Other analysis sections
  pivot_points: ['daily', 'weekly', 'monthly'],
  indicators_analysis: [],        // произвольная структура, просто проверяем наличие
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
  feedback: ['note', 'model_configuration', 'missed_data', 'issues_encountered', 'suggestions']
};

/**
 * Основная функция валидации.
 * @param {object} analysis — распарсенный JSON-ответ модели.
 */
export function validateAnalysis(analysis) {
  Object.entries(sectionRequirements).forEach(([sectionName, requiredFields]) => {
    const sectionData = analysis[sectionName];

    if (sectionData == null) {
      console.warn(`Missing section: ${sectionName}`);
      return;
    }

    // Специальная обработка gap_analysis
    if (sectionName === 'gap_analysis') {
      if (!Array.isArray(sectionData.gaps)) {
        console.warn(`gap_analysis.gaps should be an array`);
      } else {
        sectionData.gaps.forEach((gap, idx) => {
          // Проверяем, что в каждом gap есть хотя бы поля start_point либо date/price_range
          if (!gap.start_point || !gap.end_point) {
            console.warn(`gap_analysis.gaps[${idx}] missing start_point/end_point`);
          }
          if (!gap.explanation) {
            console.warn(`gap_analysis.gaps[${idx}] missing explanation`);
          }
        });
      }
      return;
    }

    // Массивы объектов
    if (Array.isArray(sectionData)) {
      sectionData.forEach((item, idx) => {
        requiredFields.forEach(field => {
          if (!(field in item)) {
            console.warn(`${sectionName}[${idx}] missing field: ${field}`);
          }
        });
      });
    }
    // Объект с вложенными разделами (pivot_points, indicators_analysis и др.)
    else if (typeof sectionData === 'object') {
      // Если нет конкретных requiredFields — просто проверяем наличие секции
      if (requiredFields.length === 0) {
        return;
      }
      requiredFields.forEach(field => {
        if (!(field in sectionData)) {
          console.warn(`${sectionName} missing field: ${field}`);
        }
      });
    }
    // Иные типы (строки, числа) — проверяем прямо
    else {
      if (requiredFields.length > 0) {
        console.warn(`${sectionName} expected keys ${requiredFields.join(', ')}, but got primitive`);
      }
    }
  });
}
