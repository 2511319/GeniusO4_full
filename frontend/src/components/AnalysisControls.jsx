// src/components/AnalysisControls.jsx
import React, { useState, Fragment } from 'react';
import PropTypes from 'prop-types';
import { Listbox, Transition } from '@headlessui/react';
import Button from './Button';
import Spinner from './Spinner';

export default function AnalysisControls({
  symbol,
  setSymbol,
  interval,
  onIntervalChange,
  limit,
  onLimitChange,
  onAnalyze,
  onLoadTest,
}) {
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      await onAnalyze({ symbol, interval, limit });
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="flex items-center gap-2 p-2 bg-gray-50">
      <div>
        <label className="block text-xs text-gray-600">Symbol</label>
        <select
          className="border border-gray-300 rounded px-2 py-1 text-sm"
          value={symbol}
          onChange={e => setSymbol(e.target.value)}
        >
          <option value="BTCUSDT">BTCUSDT</option>
          <option value="ETHUSDT">ETHUSDT</option>
          <option value="BNBUSDT">BNBUSDT</option>
        </select>
      </div>

      <div className="relative">
        <Listbox value={interval} onChange={onIntervalChange}>
          {({ open }) => (
            <>
              <Listbox.Button className="w-20 border border-gray-300 rounded px-2 py-1 text-sm text-left">
                {interval}
              </Listbox.Button>
              <Transition
                as={Fragment}
                leave="transition ease-in duration-100"
                leaveFrom="opacity-100"
                leaveTo="opacity-0"
              >
                <Listbox.Options className="absolute mt-1 max-h-60 w-20 overflow-auto rounded-md bg-white py-1 text-sm shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                  {['1m','5m','1h','4h','1d'].map(i => (
                    <Listbox.Option
                      key={i}
                      value={i}
                      className={({ active }) =>
                        `${active ? 'bg-blue-100 text-blue-900' : 'text-gray-900'} cursor-default select-none relative py-1 pl-2 pr-4`
                      }
                    >
                      {i}
                    </Listbox.Option>
                  ))}
                </Listbox.Options>
              </Transition>
            </>
          )}
        </Listbox>
      </div>

      <div>
        <label className="block text-xs text-gray-600">Limit</label>
        <input
          type="number"
          className="border border-gray-300 rounded px-2 py-1 w-20 text-sm"
          value={limit}
          onChange={e => onLimitChange(Number(e.target.value))}
        />
      </div>

      <Button onClick={handleAnalyze} disabled={loading}>
        {loading ? (
          <div className="w-6 h-6 rounded-full flex items-center justify-center">
            <Spinner size={16} />
          </div>
        ) : (
          'Analyze'
        )}
      </Button>

      {import.meta.env.DEV && (
        <Button variant="secondary" onClick={onLoadTest}>
          Load Test
        </Button>
      )}
    </div>
  );
}

AnalysisControls.propTypes = {
  symbol:     PropTypes.string.isRequired,
  setSymbol:  PropTypes.func.isRequired,
  interval:   PropTypes.string.isRequired,
  onIntervalChange:PropTypes.func.isRequired,
  limit:      PropTypes.number.isRequired,
  onLimitChange: PropTypes.func.isRequired,
  onAnalyze:  PropTypes.func.isRequired,
  onLoadTest: PropTypes.func.isRequired,
};
