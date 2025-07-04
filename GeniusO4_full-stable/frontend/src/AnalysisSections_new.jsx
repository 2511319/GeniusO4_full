import React from 'react';

// Полный список всех возможных разделов анализа
const ALL_ANALYSIS_SECTIONS = [
  { key: 'primary_analysis', title: 'Первичный анализ', category: 'basic' },
  { key: 'confidence_in_trading_decisions', title: 'Уверенность в решениях', category: 'basic' },
  { key: 'support_resistance_levels', title: 'Уровни поддержки и сопротивления', category: 'technical' },
  { key: 'trend_lines', title: 'Линии тренда', category: 'technical' },
  { key: 'fibonacci_analysis', title: 'Анализ Фибоначчи', category: 'technical' },
  { key: 'elliott_wave_analysis', title: 'Волны Эллиота', category: 'technical' },
  { key: 'unfinished_zones', title: 'Незавершенные зоны', category: 'advanced' },
  { key: 'imbalances', title: 'Дисбалансы', category: 'advanced' },
  { key: 'divergence_analysis', title: 'Анализ дивергенций', category: 'advanced' },
  { key: 'structural_edge', title: 'Структурные преимущества', category: 'advanced' },
  { key: 'candlestick_patterns', title: 'Свечные паттерны', category: 'patterns' },
  { key: 'anomalous_candles', title: 'Аномальные свечи', category: 'patterns' },
  { key: 'gap_analysis', title: 'Анализ гэпов', category: 'patterns' },
  { key: 'psychological_levels', title: 'Психологические уровни', category: 'patterns' },
  { key: 'fair_value_gaps', title: 'Зоны справедливой стоимости', category: 'advanced' },
  { key: 'indicators_analysis', title: 'Анализ индикаторов', category: 'indicators' },
  { key: 'volume_analysis', title: 'Анализ объемов', category: 'indicators' },
  { key: 'momentum_analysis', title: 'Анализ моментума', category: 'indicators' },
  { key: 'volatility_analysis', title: 'Анализ волатильности', category: 'indicators' },
  { key: 'correlation_analysis', title: 'Корреляционный анализ', category: 'advanced' },
  { key: 'market_structure', title: 'Структура рынка', category: 'advanced' },
  { key: 'liquidity_analysis', title: 'Анализ ликвидности', category: 'advanced' },
  { key: 'order_flow_analysis', title: 'Анализ потока ордеров', category: 'advanced' },
  { key: 'sentiment_analysis', title: 'Анализ настроений', category: 'advanced' },
  { key: 'recommendations', title: 'Рекомендации', category: 'basic' },
  { key: 'price_prediction', title: 'Прогноз цены', category: 'basic' },
  { key: 'risk_assessment', title: 'Оценка рисков', category: 'basic' }
];

// Группировка разделов по категориям
const categoryTitles = {
  basic: 'Основные результаты',
  technical: 'Технический анализ',
  indicators: 'Индикаторы',
  patterns: 'Паттерны',
  advanced: 'Продвинутый анализ'
};

function AnalysisSections({ analysis, activeLayers = [] }) {
  if (!analysis || Object.keys(analysis).length === 0) {
    return (
      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
        <div className="text-4xl mb-2">📊</div>
        <p>Запустите анализ для получения результатов</p>
      </div>
    );
  }

  // Функция для определения, показывать ли раздел
  const shouldShowSection = (key) => {
    const value = analysis[key];
    if (!value) return false;
    
    // Показываем если есть данные
    if (typeof value === 'string' && value.trim()) return true;
    if (typeof value === 'object' && Object.keys(value).length > 0) return true;
    if (Array.isArray(value) && value.length > 0) return true;
    
    return false;
  };

  // Группировка разделов по категориям
  const groupedSections = ALL_ANALYSIS_SECTIONS.reduce((acc, section) => {
    if (!acc[section.category]) {
      acc[section.category] = [];
    }
    acc[section.category].push(section);
    return acc;
  }, {});

  // Функция для форматирования значений
  const formatValue = (value, key) => {
    if (!value) return 'Нет данных';
    
    if (typeof value === 'string') {
      return value;
    }
    
    if (Array.isArray(value)) {
      return value.map((item, index) => (
        <div key={index} className="mb-2 p-2 bg-gray-100 dark:bg-gray-700 rounded">
          {formatObjectValue(item, index)}
        </div>
      ));
    }
    
    if (typeof value === 'object') {
      return formatObjectValue(value, key);
    }
    
    return String(value);
  };

  // Функция для форматирования объектов
  const formatObjectValue = (obj, key) => {
    if (!obj || typeof obj !== 'object') return String(obj);

    // Приоритет для поля explanation
    if (obj.explanation) {
      return (
        <div>
          <div className="mb-2 italic text-gray-700 dark:text-gray-300 text-sm">
            {obj.explanation}
          </div>
          {Object.entries(obj).filter(([k]) => k !== 'explanation').map(([subKey, subValue]) => (
            <div key={subKey} className="mb-1">
              <span className="font-bold text-blue-600 dark:text-blue-400 text-xs">
                {subKey.replace(/_/g, ' ')}:
              </span>
              <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                {typeof subValue === 'object' ? JSON.stringify(subValue, null, 2) : String(subValue)}
              </span>
            </div>
          ))}
        </div>
      );
    }

    return Object.entries(obj).map(([subKey, subValue]) => (
      <div key={subKey} className="mb-1">
        <span className="font-bold text-blue-600 dark:text-blue-400 text-xs">
          {subKey.replace(/_/g, ' ')}:
        </span>
        <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
          {typeof subValue === 'object' ? JSON.stringify(subValue, null, 2) : String(subValue)}
        </span>
      </div>
    ));
  };

  return (
    <div className="w-full">
      {Object.entries(groupedSections).map(([category, sections]) => {
        const visibleSections = sections.filter(section =>
          analysis[section.key] && shouldShowSection(section.key)
        );

        if (visibleSections.length === 0) return null;

        return (
          <div key={category} className="mb-4">
            <h3 className="mb-2 text-blue-600 dark:text-blue-400 font-bold text-sm">
              {categoryTitles[category]}
            </h3>
            <hr className="mb-3 border-gray-200 dark:border-gray-600" />

            {visibleSections.map(({ key, title }) => {
              const value = analysis[key];

              return (
                <div key={key} className="mb-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 card-modern-dark shadow-modern-dark">
                  <div className="p-3 border-b border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-sm text-gray-900 dark:text-white">
                        {title}
                      </span>
                      {activeLayers.includes(key) && (
                        <span className="text-blue-600 dark:text-blue-400 text-xs animate-pulse-glow">●</span>
                      )}
                    </div>
                  </div>

                  <div className="p-4">
                    <div className="whitespace-pre-wrap text-xs leading-relaxed text-gray-700 dark:text-gray-300">
                      {formatValue(value, key)}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        );
      })}
    </div>
  );
}

export default AnalysisSections;
