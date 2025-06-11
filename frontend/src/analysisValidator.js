export function validateAnalysis(analysis) {
  if (!analysis || typeof analysis !== 'object') return;

  const sections = {
    primary_analysis: ['global_trend', 'local_trend', 'patterns', 'anomalies'],
    unfinished_zones: ['type', 'level', 'date'],
    imbalances: ['type', 'start_point', 'end_point', 'price_range'],
    fibonacci_analysis: ['based_on_local_trend', 'based_on_global_trend'],
    elliott_wave_analysis: ['current_wave', 'wave_count', 'forecast'],
    structural_edge: ['type', 'date', 'price'],
    candlestick_patterns: ['type'],
    divergence_analysis: ['indicator', 'type', 'date'],
    fair_value_gaps: ['date', 'price_range'],
    gap_analysis: ['gaps', 'comment'],
    psychological_levels: ['levels'],
    anomalous_candles: ['date', 'type', 'price'],
    price_prediction: ['forecast', 'virtual_candles'],
    recommendations: ['trading_strategies'],
  };

  for (const [key, fields] of Object.entries(sections)) {
    const value = analysis[key];
    if (!value) continue;

    if (Array.isArray(value)) {
      value.forEach((item, i) => {
        if (typeof item !== 'object') {
          console.warn(`Раздел ${key}: запись ${i} имеет некорректный формат`);
          return;
        }
        fields.forEach((f) => {
          if (!(f in item)) {
            console.warn(`Раздел ${key}: запись ${i} отсутствует поле ${f}`);
          }
        });
        if (
          (key === 'unfinished_zones' || key === 'gap_analysis') &&
          (!item.start_point || !item.end_point)
        ) {
          console.warn('Нехватка координат для ' + key);
        }
      });
    } else if (typeof value === 'object') {
      fields.forEach((f) => {
        if (!(f in value)) {
          console.warn(`Раздел ${key}: отсутствует поле ${f}`);
        }
      });
      if (key === 'unfinished_zones' && (!value.start_point || !value.end_point)) {
        console.warn('Нехватка координат для unfinished_zones');
      }
      if (key === 'gap_analysis' && Array.isArray(value.gaps)) {
        value.gaps.forEach((gap, i) => {
          if (!gap.date) {
            console.warn(`gap_analysis: запись ${i} не содержит временной границы`);
          }
          if (!gap.start_point || !gap.end_point) {
            console.warn('Нехватка координат для gap_analysis');
          }
        });
      }
    }
  }
}

