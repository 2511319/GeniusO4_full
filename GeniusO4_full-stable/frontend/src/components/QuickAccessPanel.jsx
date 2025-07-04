import React, { useState, useEffect } from 'react';
import { getHighPriorityIndicators, getIndicatorIcon } from '../utils/indicatorManager';

const QuickAccessPanel = ({ analysis, onQuickAction, isDarkMode }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [notifications, setNotifications] = useState([]);

  // Быстрые действия для торговых рекомендаций
  const quickActions = [
    {
      id: 'view_recommendations',
      label: 'Рекомендации',
      icon: '💡',
      shortcut: 'R',
      color: 'green',
      priority: 1
    },
    {
      id: 'view_prediction',
      label: 'Прогноз',
      icon: '🔮',
      shortcut: 'P',
      color: 'blue',
      priority: 2
    },
    {
      id: 'export_analysis',
      label: 'Экспорт',
      icon: '📤',
      shortcut: 'E',
      color: 'gray',
      priority: 3
    },
    {
      id: 'share_analysis',
      label: 'Поделиться',
      icon: '📋',
      shortcut: 'S',
      color: 'purple',
      priority: 4
    }
  ];

  // Обработка горячих клавиш
  useEffect(() => {
    const handleKeyPress = (event) => {
      // Проверяем что не в поле ввода
      if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
        return;
      }

      const key = event.key.toLowerCase();
      const action = quickActions.find(a => a.shortcut.toLowerCase() === key);
      
      if (action && event.altKey) {
        event.preventDefault();
        handleQuickAction(action.id);
        showNotification(`Быстрое действие: ${action.label}`, 'success');
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, []);

  const handleQuickAction = (actionId) => {
    if (onQuickAction) {
      onQuickAction(actionId);
    }
  };

  const showNotification = (message, type = 'info') => {
    const notification = {
      id: Date.now(),
      message,
      type,
      timestamp: new Date()
    };
    
    setNotifications(prev => [...prev, notification]);
    
    // Автоматически убираем уведомление через 3 секунды
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== notification.id));
    }, 3000);
  };

  const getActionColorClasses = (color, isActive = false) => {
    const colors = {
      green: isActive 
        ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 border-green-300 dark:border-green-600'
        : 'hover:bg-green-50 dark:hover:bg-green-900/20 text-green-700 dark:text-green-400',
      blue: isActive
        ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 border-blue-300 dark:border-blue-600'
        : 'hover:bg-blue-50 dark:hover:bg-blue-900/20 text-blue-700 dark:text-blue-400',
      gray: isActive
        ? 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300 border-gray-300 dark:border-gray-600'
        : 'hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-400',
      purple: isActive
        ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300 border-purple-300 dark:border-purple-600'
        : 'hover:bg-purple-50 dark:hover:bg-purple-900/20 text-purple-700 dark:text-purple-400'
    };
    return colors[color] || colors.gray;
  };

  const hasRecommendations = analysis?.recommendations;
  const hasPrediction = analysis?.price_prediction;

  return (
    <>
      {/* Адаптивная панель быстрого доступа */}
      <div className={`fixed z-50 transition-all duration-500 animate-slide-in-right
        ${isExpanded ? 'w-72 sm:w-80' : 'w-14 sm:w-16'}
        sm:top-1/2 sm:right-6 sm:transform sm:-translate-y-1/2
        top-auto bottom-20 right-4 sm:bottom-auto
      `}>
        <div className="card-chartgenius shadow-glow-primary border-2 border-blue-200 dark:border-blue-800">
          {/* Улучшенная кнопка разворачивания */}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="w-full p-4 flex items-center justify-center btn-chartgenius-primary hover:shadow-glow-primary rounded-t-lg transition-all duration-300 animate-pulse-glow"
            title="Быстрый доступ к торговым инструментам (Alt+Q)"
          >
            <span className="text-2xl">⚡</span>
            {isExpanded && (
              <span className="ml-3 text-sm font-bold text-white">
                Торговые инструменты
              </span>
            )}
          </button>

          {/* Улучшенные действия */}
          {isExpanded && (
            <div className="p-3 space-y-2">
              {quickActions.map((action) => {
                const isDisabled =
                  (action.id === 'view_recommendations' && !hasRecommendations) ||
                  (action.id === 'view_prediction' && !hasPrediction);

                const getButtonClass = () => {
                  if (isDisabled) return 'opacity-50 cursor-not-allowed bg-gray-100 dark:bg-gray-700 text-gray-400';

                  switch(action.color) {
                    case 'green': return 'btn-chartgenius-success hover:shadow-glow-success';
                    case 'blue': return 'gradient-info text-white hover:shadow-glow-blue';
                    case 'purple': return 'gradient-purple text-white hover:shadow-glow-purple';
                    default: return 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300';
                  }
                };

                return (
                  <button
                    key={action.id}
                    onClick={() => !isDisabled && handleQuickAction(action.id)}
                    disabled={isDisabled}
                    className={`w-full p-3 rounded-xl flex items-center justify-between text-sm font-semibold transition-all duration-300 btn-modern ${getButtonClass()}`}
                    title={`${action.label} - Быстрый доступ (Alt+${action.shortcut})`}
                  >
                    <div className="flex items-center">
                      <span className="mr-3 text-lg">{action.icon}</span>
                      <span>{action.label}</span>
                    </div>
                    <kbd className="px-2 py-1 text-xs bg-white/20 backdrop-blur-sm rounded-md font-mono">
                      Alt+{action.shortcut}
                    </kbd>
                  </button>
                );
              })}
            </div>
          )}

          {/* Статус индикаторов */}
          {isExpanded && (
            <div className="p-2 border-t border-gray-200 dark:border-gray-700">
              <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Статус:</div>
              <div className="flex items-center space-x-2">
                <div className={`flex items-center ${hasRecommendations ? 'text-green-600' : 'text-gray-400'}`}>
                  <div className={`w-2 h-2 rounded-full mr-1 ${hasRecommendations ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                  <span className="text-xs">Рекомендации</span>
                </div>
                <div className={`flex items-center ${hasPrediction ? 'text-blue-600' : 'text-gray-400'}`}>
                  <div className={`w-2 h-2 rounded-full mr-1 ${hasPrediction ? 'bg-blue-500' : 'bg-gray-300'}`}></div>
                  <span className="text-xs">Прогноз</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Уведомления */}
      <div className="fixed top-4 right-4 z-60 space-y-2">
        {notifications.map((notification) => (
          <div
            key={notification.id}
            className={`px-4 py-2 rounded-lg shadow-lg border transition-all duration-300 ${
              notification.type === 'success'
                ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 border-green-300 dark:border-green-600'
                : notification.type === 'error'
                ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 border-red-300 dark:border-red-600'
                : 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 border-blue-300 dark:border-blue-600'
            }`}
          >
            <div className="flex items-center">
              <span className="mr-2">
                {notification.type === 'success' ? '✅' : notification.type === 'error' ? '❌' : 'ℹ️'}
              </span>
              <span className="text-sm font-medium">{notification.message}</span>
            </div>
          </div>
        ))}
      </div>
    </>
  );
};

export default QuickAccessPanel;
