import React from 'react';
import {
  Accordion, AccordionSummary, AccordionDetails,
  Typography, Box, Chip, Divider, List, ListItem, ListItemText,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import RecommendationsDisplay from './RecommendationsDisplay';
import PricePredictionDisplay from './PricePredictionDisplay';
import TechnicalAnalysisDisplay from './TechnicalAnalysisDisplay';
import IndicatorsAnalysisDisplay from './IndicatorsAnalysisDisplay';
import VolumeAnalysisDisplay from './VolumeAnalysisDisplay';
import IndicatorCorrelationsDisplay from './IndicatorCorrelationsDisplay';

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
  { key: 'volatility_by_intervals', title: 'Волатильность по интервалам', category: 'indicators' },
  { key: 'indicator_correlations', title: 'Корреляции индикаторов', category: 'indicators' },
  { key: 'extended_ichimoku_analysis', title: 'Расширенный анализ Ichimoku', category: 'indicators' },
  { key: 'price_prediction', title: 'Прогноз цены', category: 'prediction' },
  { key: 'recommendations', title: 'Торговые рекомендации', category: 'prediction' },
  { key: 'feedback', title: 'Обратная связь модели', category: 'meta' },
];

export default function AnalysisSections({ analysis, activeLayers = [] }) {
  if (!analysis) return null;

  // Функция для определения, должен ли раздел отображаться на основе активных слоев
  const shouldShowSection = (sectionKey) => {
    // Базовые разделы показываем всегда
    if (['primary_analysis', 'confidence_in_trading_decisions', 'price_prediction', 'recommendations'].includes(sectionKey)) {
      return true;
    }

    // Для остальных разделов проверяем активные слои
    return activeLayers.includes(sectionKey);
  };

  // Функция для форматирования значений
  const formatValue = (value, key) => {
    if (!value) return 'Данные отсутствуют';

    // Специальные компоненты для определенных разделов
    if (key === 'recommendations') {
      return <RecommendationsDisplay recommendations={value} />;
    }

    if (key === 'price_prediction') {
      return <PricePredictionDisplay prediction={value} />;
    }

    // Технические элементы анализа
    if (['support_resistance_levels', 'trend_lines', 'fibonacci_analysis',
         'elliott_wave_analysis', 'divergence_analysis'].includes(key)) {
      return <TechnicalAnalysisDisplay data={value} type={key} />;
    }

    // Анализ индикаторов
    if (key === 'indicators_analysis') {
      return <IndicatorsAnalysisDisplay indicators={value} />;
    }

    // Анализ объемов
    if (key === 'volume_analysis') {
      return <VolumeAnalysisDisplay volumeData={value} />;
    }

    // Корреляции индикаторов
    if (key === 'indicator_correlations') {
      return <IndicatorCorrelationsDisplay correlations={value} />;
    }

    if (typeof value === 'string') {
      return value;
    }

    if (Array.isArray(value)) {
      return value.map((item, index) => (
        <Box key={index} sx={{ mb: 1, p: 1, bgcolor: 'grey.100', borderRadius: 1 }}>
          {formatObjectValue(item, index)}
        </Box>
      ));
    }

    if (typeof value === 'object') {
      return formatObjectValue(value, key);
    }

    return JSON.stringify(value, null, 2);
  };

  // Функция для форматирования объектов
  const formatObjectValue = (obj, key) => {
    if (!obj || typeof obj !== 'object') return String(obj);

    return Object.entries(obj).map(([subKey, subValue]) => (
      <Box key={subKey} sx={{ mb: 0.5 }}>
        <Typography variant="caption" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
          {subKey}:
        </Typography>
        <Typography variant="body2" component="span" sx={{ ml: 1 }}>
          {typeof subValue === 'object' ? JSON.stringify(subValue, null, 2) : String(subValue)}
        </Typography>
      </Box>
    ));
  };

  // Группировка разделов по категориям
  const groupedSections = ALL_ANALYSIS_SECTIONS.reduce((acc, section) => {
    if (!acc[section.category]) {
      acc[section.category] = [];
    }
    acc[section.category].push(section);
    return acc;
  }, {});

  const categoryTitles = {
    basic: 'Базовый анализ',
    technical: 'Технический анализ',
    advanced: 'Продвинутый анализ',
    patterns: 'Паттерны и аномалии',
    indicators: 'Индикаторы',
    prediction: 'Прогнозы и рекомендации',
    meta: 'Метаинформация'
  };

  return (
    <Box sx={{ width: '100%' }}>
      {Object.entries(groupedSections).map(([category, sections]) => {
        const visibleSections = sections.filter(section =>
          analysis[section.key] && shouldShowSection(section.key)
        );

        if (visibleSections.length === 0) return null;

        return (
          <Box key={category} sx={{ mb: 2 }}>
            <Typography variant="h6" sx={{ mb: 1, color: 'primary.main' }}>
              {categoryTitles[category]}
            </Typography>
            <Divider sx={{ mb: 1 }} />

            {visibleSections.map(({ key, title }) => {
              const value = analysis[key];

              return (
                <Accordion key={key} defaultExpanded={category === 'basic'}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle1">{title}</Typography>
                      {activeLayers.includes(key) && (
                        <Chip label="Активен" size="small" color="primary" />
                      )}
                    </Box>
                  </AccordionSummary>

                  <AccordionDetails>
                    <Box sx={{ whiteSpace: 'pre-wrap' }}>
                      {formatValue(value, key)}
                    </Box>
                  </AccordionDetails>
                </Accordion>
              );
            })}
          </Box>
        );
      })}
    </Box>
  );
}

