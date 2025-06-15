import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import Button from './Button';
import { Bars3Icon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';

export default function ChartControls({ type, onChange, setSidebarOpen, setCommentsOpen }) {
  const [selected, setSelected] = useState(type);

  useEffect(() => {
    setSelected(type);
  }, [type]);

  const handleSelect = (val) => {
    setSelected(val);
    onChange(val);
  };

  return (
    <div className="absolute top-0 left-0 z-20 px-1 py-0.5 flex items-center gap-1">
      <Button variant="icon" onClick={() => setSidebarOpen((o) => !o)}>
        <Bars3Icon className="w-4 h-4" />
      </Button>
      <Button variant="icon" onClick={() => setCommentsOpen((o) => !o)}>
        <ChatBubbleLeftRightIcon className="w-4 h-4" />
      </Button>
      <div className="flex gap-1">
        <button
          type="button"
          onClick={() => handleSelect('candles')}
          className={
            selected === 'candles'
              ? 'px-2 py-1 text-xs rounded bg-blue-500 text-white'
              : 'px-2 py-1 text-xs rounded bg-gray-100 text-gray-700 hover:bg-gray-200'
          }
        >
          Candle
        </button>
        <button
          type="button"
          onClick={() => handleSelect('heikin')}
          className={
            selected === 'heikin'
              ? 'px-2 py-1 text-xs rounded bg-blue-500 text-white'
              : 'px-2 py-1 text-xs rounded bg-gray-100 text-gray-700 hover:bg-gray-200'
          }
        >
          Heikin-Ashi
        </button>
        <button
          type="button"
          onClick={() => handleSelect('renko')}
          className={
            selected === 'renko'
              ? 'px-2 py-1 text-xs rounded bg-blue-500 text-white'
              : 'px-2 py-1 text-xs rounded bg-gray-100 text-gray-700 hover:bg-gray-200'
          }
        >
          Renko
        </button>
      </div>
    </div>
  );
}

ChartControls.propTypes = {
  type: PropTypes.oneOf(['candles', 'heikin', 'renko']).isRequired,
  onChange: PropTypes.func.isRequired,
  setSidebarOpen: PropTypes.func,
  setCommentsOpen: PropTypes.func,
};
