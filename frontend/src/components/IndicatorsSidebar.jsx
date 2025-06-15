// src/components/IndicatorsSidebar.jsx

import React from 'react';
import PropTypes from 'prop-types';
import { Disclosure } from '@headlessui/react';
import { ChevronUpIcon } from '@heroicons/react/24/outline';

import groups, {
  overlays,
  volume,
  momentum,
  volatility,
  macd,
  modelAnalysis,
  forecast,
} from '../data/indicatorGroups';

export default function IndicatorsSidebar({ activeLayers, setActiveLayers }) {
  const toggle = (key) => {
    setActiveLayers(prev =>
      prev.includes(key)
        ? prev.filter(k => k !== key)
        : [...prev, key]
    );
  };

  const renderGroup = (title, keys) => (
    <Disclosure as="div" key={title} defaultOpen>
      {({ open }) => (
        <>
          <Disclosure.Button className="w-full flex justify-between items-center py-1 text-sm font-medium">
            <span>{title}</span>
            <ChevronUpIcon
              className={`w-4 h-4 transition-transform ${open ? 'rotate-180' : ''}`}
            />
          </Disclosure.Button>
          <Disclosure.Panel className="pl-2 space-y-1">
            {keys.map(key => (
              <label key={key} className="flex items-center gap-1 text-sm">
                <input
                  type="checkbox"
                  checked={activeLayers.includes(key)}
                  onChange={() => toggle(key)}
                  className="rounded"
                />
                {key}
              </label>
            ))}
          </Disclosure.Panel>
        </>
      )}
    </Disclosure>
  );

  return (
    <div className="w-60 h-full fixed left-0 top-0 bg-white shadow overflow-y-auto p-2 transition-transform">
      {renderGroup('Overlays', overlays)}
      {renderGroup('Volume', volume)}
      {renderGroup('Momentum', momentum)}
      {renderGroup('Volatility', volatility)}
      {renderGroup('MACD', macd)}
      {renderGroup('Model Analysis', modelAnalysis)}
      {renderGroup('Forecast', forecast)}
    </div>
  );
}

IndicatorsSidebar.propTypes = {
  activeLayers:  PropTypes.arrayOf(PropTypes.string).isRequired,
  setActiveLayers: PropTypes.func.isRequired,
};
