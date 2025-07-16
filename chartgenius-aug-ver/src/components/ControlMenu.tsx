// D:/project/chartgenius-gemini-ver/src/components/ControlMenu.tsx
import React from 'react';

interface ControlMenuProps {
  items: string[];
  toggles: { [key: string]: boolean };
  onToggle: (item: string) => void;
}

const ControlMenu: React.FC<ControlMenuProps> = ({ items, toggles, onToggle }) => {
  return (
    <div className="absolute top-full left-0 mt-2 w-64 p-4 bg-[#2a2a2a] border border-gray-700 rounded-lg shadow-2xl z-10">
      <div className="space-y-3">
        {items.map(item => (
          <label key={item} className="flex items-center justify-between text-sm text-gray-200 cursor-pointer hover:text-white">
            <span>{item}</span>
            <input
              type="checkbox"
              className="form-checkbox h-4 w-4 bg-gray-700 border-gray-600 rounded text-blue-500 focus:ring-blue-500"
              checked={toggles[item] || false}
              onChange={() => onToggle(item)}
            />
          </label>
        ))}
      </div>
    </div>
  );
};

export default ControlMenu;
