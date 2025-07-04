/**
 * Централизованная система управления индикаторами
 * Устраняет дублирование и обеспечивает логическую организацию
 */

import { 
  technicalIndicators, 
  advancedIndicators, 
  modelAnalysisIndicators 
} from '../indicatorGroups';

/**
 * Получить все уникальные индикаторы без дублирования
 */
export const getAllUniqueIndicators = () => {
  const allIndicators = [
    ...technicalIndicators,
    ...advancedIndicators,
    ...modelAnalysisIndicators
  ];
  
  // Удаляем дубликаты
  return [...new Set(allIndicators)];
};

/**
 * Проверить есть ли дублирование индикаторов между группами
 */
export const checkForDuplicates = () => {
  const technical = new Set(technicalIndicators);
  const advanced = new Set(advancedIndicators);
  const model = new Set(modelAnalysisIndicators);
  
  const duplicates = [];
  
  // Проверяем пересечения между группами
  for (const indicator of technical) {
    if (advanced.has(indicator)) {
      duplicates.push({ indicator, groups: ['technical', 'advanced'] });
    }
    if (model.has(indicator)) {
      duplicates.push({ indicator, groups: ['technical', 'model'] });
    }
  }
  
  for (const indicator of advanced) {
    if (model.has(indicator)) {
      duplicates.push({ indicator, groups: ['advanced', 'model'] });
    }
  }
  
  return duplicates;
};

/**
 * Получить группу индикатора
 */
export const getIndicatorGroup = (indicator) => {
  if (technicalIndicators.includes(indicator)) return 'technical';
  if (advancedIndicators.includes(indicator)) return 'advanced';
  if (modelAnalysisIndicators.includes(indicator)) return 'model';
  return 'unknown';
};

/**
 * Получить приоритет индикатора для отображения
 */
export const getIndicatorPriority = (indicator) => {
  // Модельные индикаторы имеют высший приоритет
  if (modelAnalysisIndicators.includes(indicator)) {
    if (indicator === 'recommendations') return 1;
    if (indicator === 'price_prediction') return 2;
    return 3;
  }
  
  // Продвинутые индикаторы
  if (advancedIndicators.includes(indicator)) return 4;
  
  // Технические индикаторы
  if (technicalIndicators.includes(indicator)) return 5;
  
  return 10; // Неизвестные индикаторы в конце
};

/**
 * Фильтровать индикаторы по приоритету для компактного отображения
 */
export const getHighPriorityIndicators = (indicators, maxCount = 3) => {
  return indicators
    .map(indicator => ({
      name: indicator,
      priority: getIndicatorPriority(indicator),
      group: getIndicatorGroup(indicator)
    }))
    .sort((a, b) => a.priority - b.priority)
    .slice(0, maxCount)
    .map(item => item.name);
};

/**
 * Получить описание индикатора
 */
export const getIndicatorDescription = (indicator) => {
  const descriptions = {
    // Модельные индикаторы
    'recommendations': 'Торговые рекомендации на основе комплексного анализа',
    'price_prediction': 'Прогнозирование цены с использованием ИИ моделей',
    
    // Технические индикаторы
    'RSI': 'Индекс относительной силы - осциллятор перекупленности/перепроданности',
    'MACD': 'Схождение/расхождение скользящих средних',
    'MA_20': 'Простая скользящая средняя за 20 периодов',
    'MA_50': 'Простая скользящая средняя за 50 периодов',
    'Bollinger_Bands': 'Полосы Боллинджера - индикатор волатильности',
    
    // Продвинутые индикаторы
    'support_resistance_levels': 'Уровни поддержки и сопротивления',
    'fibonacci_analysis': 'Анализ уровней Фибоначчи',
    'candlestick_patterns': 'Анализ свечных паттернов'
  };
  
  return descriptions[indicator] || `Индикатор ${indicator}`;
};

/**
 * Получить иконку для индикатора
 */
export const getIndicatorIcon = (indicator) => {
  const icons = {
    // Модельные индикаторы
    'recommendations': '💡',
    'price_prediction': '🔮',
    
    // Технические индикаторы
    'RSI': '📊',
    'MACD': '📈',
    'MA_20': '📉',
    'MA_50': '📉',
    'Bollinger_Bands': '🎯',
    
    // Продвинутые индикаторы
    'support_resistance_levels': '🏗️',
    'fibonacci_analysis': '🌀',
    'candlestick_patterns': '🕯️'
  };
  
  return icons[indicator] || '📊';
};

/**
 * Валидация конфигурации индикаторов
 */
export const validateIndicatorConfiguration = () => {
  const duplicates = checkForDuplicates();
  const allIndicators = getAllUniqueIndicators();
  
  return {
    isValid: duplicates.length === 0,
    duplicates,
    totalIndicators: allIndicators.length,
    technicalCount: technicalIndicators.length,
    advancedCount: advancedIndicators.length,
    modelCount: modelAnalysisIndicators.length
  };
};
