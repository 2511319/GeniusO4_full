import React, { useState } from 'react';
import AnalysisSections from '../AnalysisSections';
import { getHighPriorityIndicators, getIndicatorIcon, getIndicatorDescription } from '../utils/indicatorManager';

const CompactResults = ({ analysis, activeLayers, onSectionFocus }) => {
  const [expandedSection, setExpandedSection] = useState('recommendations');
  const [hoveredSection, setHoveredSection] = useState(null);

  // Приоритетные секции на основе централизованной системы управления индикаторами
  const prioritySections = [
    {
      id: 'recommendations',
      title: '💡 Торговые рекомендации',
      icon: getIndicatorIcon('recommendations'),
      color: 'green',
      priority: 1,
      description: getIndicatorDescription('recommendations')
    },
    {
      id: 'price_prediction',
      title: '📈 Прогноз цены',
      icon: getIndicatorIcon('price_prediction'),
      color: 'blue',
      priority: 2,
      description: getIndicatorDescription('price_prediction')
    },
    {
      id: 'risk_assessment',
      title: '⚠️ Оценка рисков',
      icon: '🛡️',
      color: 'yellow',
      priority: 3,
      description: 'Анализ рисков торговых позиций'
    }
  ];

  const getColorClasses = (color, isExpanded = false) => {
    const colors = {
      green: {
        bg: isExpanded ? 'bg-green-50 dark:bg-green-900/20' : 'bg-white dark:bg-gray-800',
        border: 'border-green-200 dark:border-green-700',
        text: 'text-green-800 dark:text-green-300',
        button: 'hover:bg-green-100 dark:hover:bg-green-800/30'
      },
      blue: {
        bg: isExpanded ? 'bg-blue-50 dark:bg-blue-900/20' : 'bg-white dark:bg-gray-800',
        border: 'border-blue-200 dark:border-blue-700',
        text: 'text-blue-800 dark:text-blue-300',
        button: 'hover:bg-blue-100 dark:hover:bg-blue-800/30'
      },
      yellow: {
        bg: isExpanded ? 'bg-yellow-50 dark:bg-yellow-900/20' : 'bg-white dark:bg-gray-800',
        border: 'border-yellow-200 dark:border-yellow-700',
        text: 'text-yellow-800 dark:text-yellow-300',
        button: 'hover:bg-yellow-100 dark:hover:bg-yellow-800/30'
      }
    };
    return colors[color] || colors.blue;
  };

  const toggleSection = (sectionId) => {
    setExpandedSection(expandedSection === sectionId ? null : sectionId);
    // Уведомляем родительский компонент о фокусе на секции
    if (onSectionFocus) {
      onSectionFocus(sectionId);
    }
  };

  // Tooltip компонент
  const Tooltip = ({ children, content, position = 'top' }) => {
    const [isVisible, setIsVisible] = useState(false);

    return (
      <div
        className="relative inline-block"
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
      >
        {children}
        {isVisible && content && (
          <div className={`absolute z-50 px-2 py-1 text-xs font-medium text-white bg-gray-900 dark:bg-gray-700 rounded-md shadow-lg whitespace-nowrap ${
            position === 'top' ? 'bottom-full left-1/2 transform -translate-x-1/2 mb-1' :
            position === 'bottom' ? 'top-full left-1/2 transform -translate-x-1/2 mt-1' :
            position === 'left' ? 'right-full top-1/2 transform -translate-y-1/2 mr-1' :
            'left-full top-1/2 transform -translate-y-1/2 ml-1'
          }`}>
            {content}
            <div className={`absolute w-1 h-1 bg-gray-900 dark:bg-gray-700 transform rotate-45 ${
              position === 'top' ? 'top-full left-1/2 -translate-x-1/2 -mt-0.5' :
              position === 'bottom' ? 'bottom-full left-1/2 -translate-x-1/2 -mb-0.5' :
              position === 'left' ? 'left-full top-1/2 -translate-y-1/2 -ml-0.5' :
              'right-full top-1/2 -translate-y-1/2 -mr-0.5'
            }`}></div>
          </div>
        )}
      </div>
    );
  };

  if (!analysis) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
        <div className="text-center text-gray-500 dark:text-gray-400">
          <div className="text-4xl mb-2">📊</div>
          <p className="text-sm">Запустите анализ для получения результатов</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3 animate-fade-in-up">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
        <span className="animate-pulse-glow">📋</span>
        <span className="text-gradient">Результаты анализа</span>
        <div className="ml-auto text-xs text-gray-500 dark:text-gray-400 glass-effect-dark px-2 py-1 rounded-full">
          Приоритетные данные
        </div>
      </h2>

      {/* Приоритетные секции */}
      {prioritySections.map((section) => {
        const hasData = analysis[section.id];
        const isExpanded = expandedSection === section.id;
        const colorClasses = getColorClasses(section.color, isExpanded);

        if (!hasData) return null;

        return (
          <div
            key={section.id}
            className={`card-modern-dark rounded-lg border shadow-modern-dark transition-all duration-300 ${colorClasses.bg} ${colorClasses.border} ${
              section.priority === 1 ? 'ring-2 ring-green-400 dark:ring-green-500 shadow-glow-green' : ''
            } ${section.priority === 2 ? 'shadow-glow-blue' : ''} animate-scale-in`}
            onMouseEnter={() => setHoveredSection(section.id)}
            onMouseLeave={() => setHoveredSection(null)}
            style={{ animationDelay: `${section.priority * 0.1}s` }}
          >
            <Tooltip
              content={section.description}
              position="left"
            >
              <button
                onClick={() => toggleSection(section.id)}
                className={`w-full p-3 text-left transition-all duration-200 ${colorClasses.button} ${
                  hoveredSection === section.id ? 'transform scale-[1.02]' : ''
                }`}
                aria-expanded={isExpanded}
                aria-label={`${section.title} - ${section.description}`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-lg">{section.icon}</span>
                    <div className="flex flex-col">
                      <span className={`font-medium text-sm ${colorClasses.text}`}>
                        {section.title}
                      </span>
                      {section.priority === 1 && (
                        <span className="text-xs text-green-600 dark:text-green-400 font-medium">
                          Приоритет
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {/* Индикатор статуса */}
                    <div className={`w-2 h-2 rounded-full ${
                      hasData ? 'bg-green-500' : 'bg-gray-300'
                    }`} title={hasData ? 'Данные доступны' : 'Нет данных'}></div>

                    <span className={`text-xs transition-transform duration-200 ${
                      isExpanded ? 'rotate-180' : ''
                    } ${colorClasses.text}`}>
                      ▼
                    </span>
                  </div>
                </div>
              </button>
            </Tooltip>

            {isExpanded && (
              <div className="px-3 pb-3 border-t border-gray-200 dark:border-gray-700">
                <div className="mt-2 max-h-64 overflow-y-auto">
                  <AnalysisSections
                    analysis={{ [section.id]: analysis[section.id] }}
                    activeLayers={[section.id]}
                  />
                </div>
              </div>
            )}
          </div>
        );
      })}

      {/* Остальные результаты в компактном виде */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="p-3 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-sm font-medium text-gray-900 dark:text-white">
            📈 Дополнительные индикаторы
          </h3>
        </div>
        <div className="p-3 max-h-96 overflow-y-auto">
          <AnalysisSections 
            analysis={analysis} 
            activeLayers={activeLayers.filter(layer => 
              !prioritySections.some(section => section.id === layer)
            )} 
          />
        </div>
      </div>

      {/* Быстрые действия */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-3">
        <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
          ⚡ Быстрые действия
        </h3>
        <div className="space-y-2">
          <button className="w-full text-left px-2 py-1 text-xs text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-colors">
            📤 Экспорт результатов
          </button>
          <button className="w-full text-left px-2 py-1 text-xs text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-colors">
            📋 Копировать рекомендации
          </button>
          <button className="w-full text-left px-2 py-1 text-xs text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-colors">
            🔔 Настроить уведомления
          </button>
        </div>
      </div>
    </div>
  );
};

export default CompactResults;
