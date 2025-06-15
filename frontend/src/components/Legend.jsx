// src/components/Legend.jsx

import React from 'react';
import PropTypes from 'prop-types';

/**
 * Legend — простая легенда, в которую передаётся массив meta:
 * [{ key, name, color, dashed, icon, visible }, ...]
 */
export default function Legend({ meta = [], orientation = 'vertical' }) {  // meta по умолчанию = []
  return (
    <div className="absolute bottom-0 left-0 z-20 bg-white max-h-[200px] overflow-y-auto p-1 rounded">
      <h6 className="text-xs font-semibold mb-1">Legend</h6>
      <ul
        className={`flex ${orientation === 'horizontal' ? 'flex-row flex-wrap' : 'flex-col'} list-none p-0 m-0`}
      >
        {meta.map(item => (
          <li
            key={item.key}
            onClick={item.onToggle}  // onToggle можно добавить в meta
            className="flex items-center cursor-pointer px-1 py-0.5"
          >
            <span
              className="inline-block w-3 h-3 mr-1"
              style={{
                backgroundColor: item.color,
                border: item.dashed ? '1px dashed' : 'none',
              }}
            >
              {item.icon && <span className="text-[10px]">{item.icon}</span>}
            </span>
            <span className={item.visible ? '' : 'line-through'}>{item.name}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

Legend.propTypes = {
  meta: PropTypes.arrayOf(PropTypes.shape({
    key:     PropTypes.string.isRequired,
    name:    PropTypes.string.isRequired,
    color:   PropTypes.string,
    dashed:  PropTypes.bool,
    icon:    PropTypes.string,
    visible: PropTypes.bool,
    onToggle:PropTypes.func,
  })),
  orientation: PropTypes.oneOf(['vertical', 'horizontal']),
};
