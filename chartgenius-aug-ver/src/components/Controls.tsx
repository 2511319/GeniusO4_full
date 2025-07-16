// D:/project/chartgenius-gemini-ver/src/components/Controls.tsx
import React, { useState } from 'react';
import ControlMenu from './ControlMenu';

// ... (определение controlGroups остается тем же)
const controlGroups = {
  trendsAndLevels: {
    label: 'Тренды и Уровни',
    icon: '📈',
    items: [
      'Уровни поддержки/сопротивления', 'Линии тренда', 'Скользящие средние', 
      'Полосы Боллинджера', 'Parabolic SAR', 'VWAP', 'Конверты MA', 'Облако Ишимоку',
    ],
  },
  oscillatorsAndVolume: {
    label: 'Осцилляторы и Объем',
    icon: '📊',
    items: [
      'Объем', 'RSI', 'MACD', 'Stochastic', 'Williams %R', 'ADX', 'ATR', 'OBV',
    ],
  },
  aiStructures: {
    label: 'Структуры AI',
    icon: '✨',
    items: [
      'Коррекция по Фибоначчи', 'Зоны дисбаланса', 'Незавершенные зоны', 
      'Свечные паттерны', 'Дивергенции', 'Волны Эллиотта',
    ],
  },
  recommendationsAndForecast: {
    label: 'Рекомендации и Прогноз',
    icon: '🔮',
    items: ['Визуальный прогноз', 'Показать сделки'],
  },
};


interface ControlsProps {
  toggles: { [key: string]: boolean };
  onToggle: (item: string) => void;
}

const Controls: React.FC<ControlsProps> = ({ toggles, onToggle }) => {
  const [activeMenu, setActiveMenu] = useState<string | null>(null);

  const handleMenuToggle = (menuKey: string) => {
    setActiveMenu(prev => (prev === menuKey ? null : menuKey));
  };

  return (
    <div className="relative flex items-center gap-2 p-2 bg-[#1a1a1a] border-b border-gray-800">
      {Object.entries(controlGroups).map(([key, { label, icon, items }]) => (
        <div key={key} className="relative">
          <button
            onClick={() => handleMenuToggle(key)}
            className={`flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
              activeMenu === key
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700/50 hover:bg-gray-700 text-gray-300'
            }`}
          >
            <span>{icon}</span>
            {label}
          </button>
          {activeMenu === key && (
            <ControlMenu 
              items={items} 
              toggles={toggles}
              onToggle={onToggle}
            />
          )}
        </div>
      ))}
    </div>
  );
};

export default Controls;
