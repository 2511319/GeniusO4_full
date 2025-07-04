import React from 'react';

// Компонент скелетона для загрузки
export const SkeletonLoader = ({ className = '', lines = 3 }) => {
  return (
    <div className={`animate-pulse ${className}`}>
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className={`bg-gray-200 dark:bg-gray-700 rounded ${
            index === lines - 1 ? 'w-3/4' : 'w-full'
          } h-4 mb-2`}
        />
      ))}
    </div>
  );
};

// Индикатор прогресса анализа
export const AnalysisProgress = ({ progress = 0, stage = '', isDarkMode = false }) => {
  const stages = [
    { id: 'data', label: 'Загрузка данных', icon: '📊' },
    { id: 'technical', label: 'Технический анализ', icon: '📈' },
    { id: 'advanced', label: 'Продвинутый анализ', icon: '🔍' },
    { id: 'ai', label: 'ИИ анализ', icon: '🤖' },
    { id: 'complete', label: 'Завершение', icon: '✅' }
  ];

  const currentStageIndex = stages.findIndex(s => s.id === stage);
  const progressPercent = Math.min(100, Math.max(0, progress));

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Анализ в процессе
        </h3>
        <span className="text-sm text-gray-500 dark:text-gray-400">
          {progressPercent.toFixed(0)}%
        </span>
      </div>

      {/* Прогресс-бар */}
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-6">
        <div
          className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-500 ease-out"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Этапы */}
      <div className="space-y-3">
        {stages.map((stageItem, index) => {
          const isActive = index === currentStageIndex;
          const isCompleted = index < currentStageIndex;
          const isPending = index > currentStageIndex;

          return (
            <div
              key={stageItem.id}
              className={`flex items-center space-x-3 p-2 rounded-md transition-all duration-300 ${
                isActive
                  ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700'
                  : isCompleted
                  ? 'bg-green-50 dark:bg-green-900/20'
                  : 'bg-gray-50 dark:bg-gray-700/50'
              }`}
            >
              <div
                className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                  isActive
                    ? 'bg-blue-500 text-white animate-pulse'
                    : isCompleted
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-300 dark:bg-gray-600 text-gray-600 dark:text-gray-400'
                }`}
              >
                {isCompleted ? '✓' : stageItem.icon}
              </div>
              <span
                className={`font-medium ${
                  isActive
                    ? 'text-blue-700 dark:text-blue-300'
                    : isCompleted
                    ? 'text-green-700 dark:text-green-300'
                    : 'text-gray-500 dark:text-gray-400'
                }`}
              >
                {stageItem.label}
              </span>
              {isActive && (
                <div className="ml-auto">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Дополнительная информация */}
      <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-md">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          💡 <strong>Совет:</strong> Используйте Alt+R для быстрого доступа к рекомендациям после завершения анализа
        </p>
      </div>
    </div>
  );
};

// Компонент ошибки с возможностью повтора
export const ErrorState = ({ error, onRetry, isDarkMode = false }) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-red-200 dark:border-red-700 p-6">
      <div className="flex items-center space-x-3 mb-4">
        <div className="flex-shrink-0">
          <div className="w-10 h-10 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center">
            <span className="text-red-600 dark:text-red-400 text-xl">⚠️</span>
          </div>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-red-800 dark:text-red-300">
            Ошибка анализа
          </h3>
          <p className="text-sm text-red-600 dark:text-red-400">
            Произошла ошибка при выполнении анализа
          </p>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 rounded-md border border-red-200 dark:border-red-700">
          <p className="text-sm text-red-700 dark:text-red-300 font-mono">
            {error.message || error.toString()}
          </p>
        </div>
      )}

      <div className="flex space-x-3">
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md font-medium transition-colors duration-200 flex items-center space-x-2"
        >
          <span>🔄</span>
          <span>Повторить</span>
        </button>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md font-medium transition-colors duration-200"
        >
          Перезагрузить страницу
        </button>
      </div>

      <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-md">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          <strong>Возможные причины:</strong>
        </p>
        <ul className="text-sm text-gray-600 dark:text-gray-400 mt-1 space-y-1">
          <li>• Проблемы с подключением к серверу</li>
          <li>• Недоступность данных для выбранного символа</li>
          <li>• Временная перегрузка системы</li>
        </ul>
      </div>
    </div>
  );
};

// Пустое состояние с призывом к действию
export const EmptyState = ({ onAction, isDarkMode = false }) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-8 text-center">
      <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
        <span className="text-3xl">📊</span>
      </div>
      
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
        Готов к анализу
      </h3>
      
      <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
        Выберите параметры и запустите анализ для получения торговых рекомендаций и прогнозов
      </p>

      <div className="space-y-3">
        <button
          onClick={onAction}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors duration-200 flex items-center space-x-2 mx-auto"
        >
          <span>🚀</span>
          <span>Запустить анализ</span>
        </button>
        
        <div className="text-sm text-gray-500 dark:text-gray-400">
          Или используйте <kbd className="px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded text-xs">Enter</kbd> для быстрого запуска
        </div>
      </div>

      <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-700">
        <h4 className="font-medium text-blue-800 dark:text-blue-300 mb-2">
          💡 Быстрые клавиши:
        </h4>
        <div className="text-sm text-blue-700 dark:text-blue-400 space-y-1">
          <div><kbd className="px-1 py-0.5 bg-blue-200 dark:bg-blue-800 rounded text-xs">Alt+R</kbd> - Просмотр рекомендаций</div>
          <div><kbd className="px-1 py-0.5 bg-blue-200 dark:bg-blue-800 rounded text-xs">Alt+P</kbd> - Просмотр прогноза</div>
          <div><kbd className="px-1 py-0.5 bg-blue-200 dark:bg-blue-800 rounded text-xs">Alt+E</kbd> - Экспорт данных</div>
        </div>
      </div>
    </div>
  );
};
