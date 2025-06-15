// src/components/CommentsPanel.jsx

import React from 'react';
import PropTypes from 'prop-types';
import { Tab } from '@headlessui/react';

function classNames(...classes) {
  return classes.filter(Boolean).join(' ');
}

/**
 * Панель комментариев
 * - Tab 1: Primary Analysis
 * - Tab 2: Explanation (explanation для activeLayers)
 */
export default function CommentsPanel({ analysis, activeLayers }) {
  const [tab, setTab] = React.useState(0);

  const primary = analysis.primary_analysis || {};
  const conf = analysis.confidence_in_trading_decisions || {};

  return (
    <div className="w-full bg-gray-100 overflow-y-auto p-2 box-border text-sm">
      <h6 className="text-xs font-semibold">Confidence: {conf.level || 'N/A'}</h6>
      <div className="text-xs text-gray-500">{conf.reason}</div>
      <hr className="my-2 border-gray-300" />

      <Tab.Group selectedIndex={tab} onChange={setTab}>
        <Tab.List className="flex space-x-2 border-b">
          <Tab
            className={({ selected }) =>
              classNames(
                'py-1 px-2 text-sm',
                selected ? 'border-b-2 border-blue-500 font-medium' : 'text-gray-600'
              )
            }
          >
            Primary Analysis
          </Tab>
          <Tab
            className={({ selected }) =>
              classNames(
                'py-1 px-2 text-sm',
                selected ? 'border-b-2 border-blue-500 font-medium' : 'text-gray-600'
              )
            }
          >
            Explanation
          </Tab>
        </Tab.List>
        <Tab.Panels>
          <Tab.Panel className="mt-2">
            {primary.global_trend && (
              <>
                <h6 className="text-sm font-semibold mt-1 mb-1">Global Trend</h6>
                <div className="text-sm mb-2">{primary.global_trend}</div>
              </>
            )}
            {primary.local_trend && (
              <>
                <h6 className="text-sm font-semibold mt-1 mb-1">Local Trend</h6>
                <div className="text-sm mb-2">{primary.local_trend}</div>
              </>
            )}
            {primary.patterns && (
              <>
                <h6 className="text-sm font-semibold mt-1 mb-1">Patterns</h6>
                <div className="text-sm mb-2">{primary.patterns}</div>
              </>
            )}
            {primary.anomalies && (
              <>
                <h6 className="text-sm font-semibold mt-1 mb-1">Anomalies</h6>
                <div className="text-sm mb-2">{primary.anomalies}</div>
              </>
            )}
          </Tab.Panel>

          <Tab.Panel className="mt-2">
            {activeLayers.map((layer) => {
              const expl = analysis[layer]?.explanation;
              if (!expl) return null;
              const title = layer
                .split('_')
                .map((w) => w[0].toUpperCase() + w.slice(1))
                .join(' ');
              return (
                <div key={layer} className="mb-2">
                  <h6 className="text-sm font-semibold mt-1 mb-1">{title}</h6>
                  <div className="text-sm">{expl}</div>
                </div>
              );
            })}
            {activeLayers.every((l) => !analysis[l]?.explanation) && (
              <div className="text-xs text-gray-500">
                No explanations for selected indicators.
              </div>
            )}
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </div>
  );
}

CommentsPanel.propTypes = {
  analysis:     PropTypes.object.isRequired,
  activeLayers: PropTypes.arrayOf(PropTypes.string).isRequired,
};
