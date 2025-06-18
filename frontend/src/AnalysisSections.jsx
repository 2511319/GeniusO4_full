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

    // Приоритет для поля explanation
    if (obj.explanation) {
      return (
        <Box sx={{
          p: 1.5,
          bgcolor: 'rgba(33, 150, 243, 0.08)',
          borderRadius: 1,
          border: '1px solid rgba(33, 150, 243, 0.2)',
          mb: 1
        }}>
          <Typography variant="body2" sx={{
            mb: 1.5,
            fontStyle: 'italic',
            color: '#e3f2fd',
            fontWeight: 500,
            lineHeight: 1.4
          }}>
            💡 {obj.explanation}
          </Typography>
          {Object.entries(obj).filter(([k]) => k !== 'explanation').map(([subKey, subValue]) => (
            <Box key={subKey} sx={{ mb: 0.8, display: 'flex', flexWrap: 'wrap', alignItems: 'baseline' }}>
              <Typography variant="caption" sx={{
                fontWeight: 'bold',
                color: '#90caf9',
                fontSize: '0.75rem',
                mr: 1,
                minWidth: 'fit-content'
              }}>
                {subKey.replace(/_/g, ' ')}:
              </Typography>
              <Typography variant="body2" component="span" sx={{
                fontSize: '0.8rem',
                color: '#ffffff',
                fontWeight: 400
              }}>
                {typeof subValue === 'object' ? JSON.stringify(subValue, null, 2) : String(subValue)}
              </Typography>
            </Box>
          ))}
        </Box>
      );
    }

    return Object.entries(obj).map(([subKey, subValue]) => (
      <Box key={subKey} sx={{
        mb: 0.8,
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'baseline',
        p: 0.8,
        bgcolor: 'rgba(255, 255, 255, 0.02)',
        borderRadius: 0.5,
        border: '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        <Typography variant="caption" sx={{
          fontWeight: 'bold',
          color: '#4fc3f7',
          fontSize: '0.75rem',
          mr: 1,
          minWidth: 'fit-content'
        }}>
          {subKey.replace(/_/g, ' ')}:
        </Typography>
        <Typography variant="body2" component="span" sx={{
          fontSize: '0.8rem',
          color: '#e0e0e0',
          fontWeight: 400
        }}>
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
          <Box key={category} sx={{ mb: 1.2 }}>
            <Box sx={{
              p: 1,
              bgcolor: 'rgba(33, 150, 243, 0.15)',
              borderRadius: 1,
              border: '1px solid rgba(33, 150, 243, 0.3)',
              mb: 0.8
            }}>
              <Typography variant="subtitle1" sx={{
                mb: 0,
                color: '#e3f2fd',
                fontWeight: 'bold',
                fontSize: '0.95rem',
                textAlign: 'center'
              }}>
                📊 {categoryTitles[category]}
              </Typography>
            </Box>

            {visibleSections.map(({ key, title }) => {
              const value = analysis[key];

              return (
                <Accordion key={key} defaultExpanded={category === 'basic'} sx={{
                  mb: 0.3,
                  bgcolor: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  '&:before': { display: 'none' }
                }}>
                  <AccordionSummary
                    expandIcon={<ExpandMoreIcon sx={{ color: '#90caf9' }} />}
                    sx={{
                      py: 0.3,
                      minHeight: 28,
                      bgcolor: 'rgba(33, 150, 243, 0.05)',
                      '& .MuiAccordionSummary-content': {
                        my: 0.3,
                        minHeight: 'unset'
                      }
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" sx={{
                        fontWeight: 600,
                        fontSize: '0.85rem',
                        color: '#e3f2fd'
                      }}>
                        {title}
                      </Typography>
                      {activeLayers.includes(key) && (
                        <Chip
                          label="●"
                          size="small"
                          color="primary"
                          sx={{
                            minWidth: 'auto',
                            height: 16,
                            fontSize: '0.7rem',
                            bgcolor: '#4caf50',
                            color: 'white'
                          }}
                        />
                      )}
                    </Box>
                  </AccordionSummary>

                  <AccordionDetails sx={{
                    py: 0.8,
                    px: 1.5,
                    bgcolor: 'rgba(0, 0, 0, 0.2)'
                  }}>
                    <Box sx={{
                      whiteSpace: 'pre-wrap',
                      fontSize: '0.8rem',
                      lineHeight: 1.3
                    }}>
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

