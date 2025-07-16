import React from 'react';

interface ElementDetailsPanelProps {
  analysisData: any;
  toggles: { [key: string]: boolean };
}

// Статические описания технических индикаторов
const TECHNICAL_INDICATORS_DESCRIPTIONS = {
  'Скользящие средние': {
    title: 'Скользящие средние (Moving Averages)',
    text: 'Скользящие средние сглаживают ценовые колебания и помогают определить направление тренда. MA20 (зеленая) - краткосрочный тренд, MA50 (синяя) - среднесрочный, MA100 (оранжевая) и MA200 (красная) - долгосрочные тренды. Когда цена выше MA - восходящий тренд, ниже - нисходящий.'
  },
  'Полосы Боллинджера': {
    title: 'Полосы Боллинджера (Bollinger Bands)',
    text: 'Полосы Боллинджера состоят из средней линии (MA20) и двух полос на расстоянии 2 стандартных отклонений. Сужение полос указывает на низкую волатильность, расширение - на высокую. Касание ценой верхней полосы может сигнализировать о перекупленности, нижней - о перепроданности.'
  },
  'Parabolic SAR': {
    title: 'Параболический SAR (Parabolic Stop and Reverse)',
    text: 'Параболический SAR помогает определить точки разворота тренда. Точки SAR ниже цены указывают на восходящий тренд, выше цены - на нисходящий. Пересечение ценой уровня SAR может сигнализировать о смене тренда и служить сигналом для входа/выхода из позиции.'
  },
  'VWAP': {
    title: 'VWAP (Volume Weighted Average Price)',
    text: 'VWAP - средневзвешенная по объему цена, показывающая справедливую стоимость актива. Цена выше VWAP указывает на бычьи настроения, ниже - на медвежьи. Институциональные трейдеры часто используют VWAP как ориентир для крупных сделок.'
  },
  'Конверты MA': {
    title: 'Конверты скользящих средних (MA Envelopes)',
    text: 'Конверты MA создают канал вокруг скользящей средней на фиксированном процентном расстоянии. Верхняя и нижняя границы помогают определить уровни перекупленности и перепроданности. Пробой границ может сигнализировать о сильном движении цены.'
  },
  'Облако Ишимоку': {
    title: 'Облако Ишимоку (Ichimoku Cloud)',
    text: 'Система Ишимоку включает линии Tenkan-sen, Kijun-sen и облако Kumo. Цена выше облака указывает на восходящий тренд, ниже - на нисходящий, внутри облака - на боковое движение. Пересечение Tenkan-sen и Kijun-sen дает сигналы входа/выхода.'
  },
  'Объем': {
    title: 'Объем торгов (Volume)',
    text: 'Объем показывает количество торгуемых активов за определенный период. Высокий объем подтверждает силу ценового движения, низкий может указывать на слабость тренда. Рост объема при пробое уровней увеличивает вероятность продолжения движения.'
  },
  'RSI': {
    title: 'RSI (Relative Strength Index)',
    text: 'RSI измеряет скорость и изменение ценовых движений в диапазоне 0-100. Значения выше 70 указывают на перекупленность (возможность продажи), ниже 30 - на перепроданность (возможность покупки). Дивергенции между RSI и ценой могут предсказывать развороты.'
  },
  'MACD': {
    title: 'MACD (Moving Average Convergence Divergence)',
    text: 'MACD состоит из основной линии (разность EMA12 и EMA26), сигнальной линии (EMA9 от основной) и гистограммы. Пересечение основной линии выше сигнальной - бычий сигнал, ниже - медвежий. Гистограмма показывает силу сигнала.'
  },
  'Stochastic': {
    title: 'Стохастический осциллятор (Stochastic)',
    text: 'Стохастик сравнивает цену закрытия с диапазоном цен за определенный период. Значения выше 80 указывают на перекупленность, ниже 20 - на перепроданность. Пересечение линий %K и %D дает торговые сигналы.'
  },
  'Стохастический': {
    title: 'Стохастический осциллятор (Stochastic)',
    text: 'Стохастик сравнивает цену закрытия с диапазоном цен за определенный период. Значения выше 80 указывают на перекупленность, ниже 20 - на перепроданность. Пересечение линий %K и %D дает торговые сигналы.'
  },
  'Williams %R': {
    title: 'Уильямс %R (Williams Percent Range)',
    text: 'Williams %R - осциллятор, показывающий положение цены закрытия относительно максимума за период. Значения выше -20 указывают на перекупленность, ниже -80 - на перепроданность. Используется для поиска точек разворота.'
  },
  'ADX': {
    title: 'ADX (Average Directional Index)',
    text: 'ADX измеряет силу тренда независимо от его направления. Значения выше 25 указывают на сильный тренд, ниже 20 - на слабый или боковое движение. ADX не показывает направление, только силу тренда.'
  },
  'АТР': {
    title: 'АТР (Average True Range)',
    text: 'АТР измеряет волатильность рынка, показывая средний диапазон движения цены. Высокие значения АТР указывают на высокую волатильность, низкие - на низкую. Используется для установки стоп-лоссов и определения размера позиции.'
  },
  'ATR': {
    title: 'ATR (Average True Range)',
    text: 'ATR измеряет волатильность рынка, показывая средний диапазон движения цены. Высокие значения ATR указывают на высокую волатильность, низкие - на низкую. Используется для установки стоп-лоссов и определения размера позиции.'
  },
  'ОБВ': {
    title: 'ОБВ (On-Balance Volume)',
    text: 'ОБВ связывает объем с изменением цены. Если цена закрытия выше предыдущей, объем добавляется к ОБВ, если ниже - вычитается. Расхождение между ОБВ и ценой может предсказывать развороты тренда.'
  },
  'OBV': {
    title: 'OBV (On-Balance Volume)',
    text: 'OBV связывает объем с изменением цены. Если цена закрытия выше предыдущей, объем добавляется к OBV, если ниже - вычитается. Расхождение между OBV и ценой может предсказывать развороты тренда.'
  }
};

const ElementDetailsPanel: React.FC<ElementDetailsPanelProps> = ({ analysisData, toggles }) => {
  // Функция для получения объяснений активных элементов
  const getActiveExplanations = () => {
    const explanations: Array<{ title: string; text: string }> = [];

    // ТЕХНИЧЕСКИЕ ИНДИКАТОРЫ - добавляем статические описания
    Object.keys(TECHNICAL_INDICATORS_DESCRIPTIONS).forEach(indicatorName => {
      if (toggles[indicatorName]) {
        const description = TECHNICAL_INDICATORS_DESCRIPTIONS[indicatorName as keyof typeof TECHNICAL_INDICATORS_DESCRIPTIONS];
        explanations.push({
          title: description.title,
          text: description.text
        });
      }
    });

    // AI-АНАЛИЗ - обрабатываем данные из analysisData
    // Уровни поддержки/сопротивления
    if (toggles['Уровни поддержки/сопротивления'] && analysisData?.support_resistance_levels) {
      const supports = analysisData.support_resistance_levels.supports || [];
      const resistances = analysisData.support_resistance_levels.resistances || [];
      
      supports.forEach((support: any) => {
        if (support.explanation) {
          explanations.push({
            title: `Поддержка ${support.level}`,
            text: support.explanation
          });
        }
      });

      resistances.forEach((resistance: any) => {
        if (resistance.explanation) {
          explanations.push({
            title: `Сопротивление ${resistance.level}`,
            text: resistance.explanation
          });
        }
      });
    }

    // Линии тренда
    if (toggles['Линии тренда'] && analysisData?.trend_lines?.lines) {
      analysisData.trend_lines.lines.forEach((line: any) => {
        explanations.push({
          title: `Трендовая линия (${line.type})`,
          text: `Линия тренда от ${line.start_point?.date} до ${line.end_point?.date}`
        });
      });
    }

    // Коррекция по Фибоначчи
    if (toggles['Коррекция по Фибоначчи'] && analysisData?.fibonacci_analysis) {
      if (analysisData.fibonacci_analysis.based_on_local_trend?.explanation) {
        explanations.push({
          title: 'Фибоначчи (локальный тренд)',
          text: analysisData.fibonacci_analysis.based_on_local_trend.explanation
        });
      }
      if (analysisData.fibonacci_analysis.based_on_global_trend?.explanation) {
        explanations.push({
          title: 'Фибоначчи (глобальный тренд)',
          text: analysisData.fibonacci_analysis.based_on_global_trend.explanation
        });
      }
    }

    // Зоны дисбаланса
    if (toggles['Зоны дисбаланса'] && analysisData?.imbalances) {
      analysisData.imbalances.forEach((imbalance: any) => {
        if (imbalance.explanation) {
          explanations.push({
            title: `Зона дисбаланса (${imbalance.type})`,
            text: imbalance.explanation
          });
        }
      });
    }

    // Незавершенные зоны
    if (toggles['Незавершенные зоны'] && analysisData?.unfinished_zones) {
      analysisData.unfinished_zones.forEach((zone: any) => {
        if (zone.explanation) {
          explanations.push({
            title: `Незавершенная зона (${zone.type})`,
            text: zone.explanation
          });
        }
      });
    }

    // Свечные паттерны
    if (toggles['Свечные паттерны'] && analysisData?.candlestick_patterns) {
      analysisData.candlestick_patterns.forEach((pattern: any) => {
        if (pattern.explanation) {
          explanations.push({
            title: `Свечной паттерн (${pattern.type})`,
            text: pattern.explanation
          });
        }
      });
    }

    // Дивергенции
    if (toggles['Дивергенции'] && analysisData?.divergence_analysis) {
      analysisData.divergence_analysis.forEach((divergence: any) => {
        if (divergence.explanation) {
          explanations.push({
            title: `Дивергенция ${divergence.indicator} (${divergence.type})`,
            text: divergence.explanation
          });
        }
      });
    }

    // Волны Эллиотта
    if (toggles['Волны Эллиотта'] && analysisData?.elliott_wave_analysis?.explanation) {
      explanations.push({
        title: 'Волны Эллиотта',
        text: analysisData.elliott_wave_analysis.explanation
      });
    }

    // Визуальный прогноз
    if (toggles['Визуальный прогноз'] && analysisData?.price_prediction?.forecast) {
      explanations.push({
        title: 'Прогноз цены',
        text: analysisData.price_prediction.forecast
      });
    }

    // Волны Эллиотта
    if (toggles['Волны Эллиотта'] && analysisData?.elliott_wave_analysis?.explanation) {
      explanations.push({
        title: 'Волны Эллиотта',
        text: analysisData.elliott_wave_analysis.explanation
      });
    }

    // Визуальный прогноз
    if (toggles['Визуальный прогноз'] && analysisData?.price_prediction?.forecast) {
      explanations.push({
        title: 'Прогноз цены',
        text: analysisData.price_prediction.forecast
      });
    }

    // Торговые рекомендации
    if (toggles['Показать сделки'] && analysisData?.recommendations?.trading_strategies) {
      analysisData.recommendations.trading_strategies.forEach((strategy: any) => {
        if (strategy.other_details) {
          explanations.push({
            title: `Стратегия: ${strategy.strategy}`,
            text: strategy.other_details
          });
        }
      });
    }

    return explanations;
  };

  const explanations = getActiveExplanations();

  if (explanations.length === 0) {
    return (
      <div className="w-80 bg-[#1a1a1a] border-l border-gray-800 p-4">
        <h3 className="text-lg font-semibold text-white mb-4">Детали элемента</h3>
        <p className="text-gray-400 text-sm">
          Включите любой элемент анализа AI или технический индикатор, чтобы увидеть подробное объяснение
        </p>
      </div>
    );
  }

  return (
    <div className="w-80 bg-[#1a1a1a] border-l border-gray-800 p-4 overflow-y-auto">
      <h3 className="text-lg font-semibold text-white mb-4">Детали элемента</h3>
      <div className="space-y-4">
        {explanations.map((explanation, index) => (
          <div key={index} className="bg-gray-800/50 rounded-lg p-3">
            <h4 className="text-sm font-medium text-blue-400 mb-2">
              {explanation.title}
            </h4>
            <p className="text-xs text-gray-300 leading-relaxed">
              {explanation.text}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ElementDetailsPanel;
