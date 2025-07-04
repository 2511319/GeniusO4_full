import React, { useState } from 'react';

const ChartToolbar = ({
  symbol,
  interval,
  onIntervalChange,
  onFullscreen,
  isDarkMode,
  onThemeToggle
}) => {
  const [chartType, setChartType] = useState('candlestick');

  const chartTypes = [
    { value: 'candlestick', label: 'Свечи', title: 'Свечной график' },
    { value: 'line', label: 'Линия', title: 'Линейный график' },
    { value: 'area', label: 'Область', title: 'Область' }
  ];

  return (
    <div className="pro-panel-compact mb-4">
      <div className="flex items-center justify-between">
        {/* Информация о символе */}
        <div className="flex items-center pro-space-x-4">
          <div className="flex items-center pro-space-x-2">
            <span className="text-lg font-semibold pro-text-primary">
              {symbol || 'Выберите актив'}
            </span>
            <span className="pro-status pro-status-success">
              Готов к анализу
            </span>
          </div>

          <div className="flex items-center pro-space-x-2">
            <span className="text-xs pro-text-muted">
              Обновлено: {new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}
            </span>
            <span className="text-xs pro-text-muted">
              Индикаторов: {Object.keys(window.activeLayers || {}).length || 0}
            </span>
          </div>
        </div>

        {/* Тип графика */}
        <div className="flex items-center pro-space-x-3">
          <span className="text-sm pro-text-secondary">Тип:</span>
          <div className="flex items-center pro-space-x-1">
            {chartTypes.map((type) => (
              <button
                key={type.value}
                onClick={() => setChartType(type.value)}
                title={type.title}
                className={`pro-btn text-sm ${
                  chartType === type.value ? 'pro-btn-primary' : ''
                }`}
              >
                {type.label}
              </button>
            ))}
          </div>
        </div>

        {/* Действия */}
        <div className="flex items-center pro-space-x-2">
          <button
            onClick={onFullscreen}
            className="pro-btn"
            title="Полный экран"
          >
            Развернуть
          </button>
          <button
            className="pro-btn pro-btn-primary"
            title="Сохранить настройки"
          >
            Сохранить
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChartToolbar;
