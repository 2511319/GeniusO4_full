// src/components/InsightsPanel.jsx

import React from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';

/**
 * Панель Insights для прочих разделов анализа:
 * indicators_analysis, volume_analysis, indicator_correlations,
 * pivot_points, risk_management, feedback
 */
export default function InsightsPanel({ analysis }) {
  // Пример вывода indicators_analysis как таблицы
  const ia = analysis.indicators_analysis || {};
  const va = analysis.volume_analysis || {};
  const ic = analysis.indicator_correlations || {};
  const pp = analysis.pivot_points || {};
  const rm = analysis.risk_management || {};
  const fb = analysis.feedback || {};

  const [show, setShow] = React.useState(false);

  React.useEffect(() => {
    if (analysis && Object.keys(analysis).length) {
      setShow(true);
    }
  }, [analysis]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={show ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }}
    >
      <div className="w-full max-h-[40%] bg-gray-50 overflow-y-auto p-1 box-border">
      <h6 className="text-sm font-semibold mt-1 mb-1">Indicators Analysis</h6>
      {Object.entries(ia).map(([key, val]) => (
        typeof val === 'object' && (
          <div key={key} className="mb-1">
            <div className="text-xs font-semibold">{key}</div>
            {Object.entries(val).map(([field, value]) => (
              <div key={field} className="text-sm">
                {field}: {value}
              </div>
            ))}
          </div>
        )
      ))}
      <hr className="my-1 border-gray-200" />

      <h6 className="text-sm font-semibold mt-1 mb-1">Volume Analysis</h6>
      {va.volume_trends && <div className="text-sm">{va.volume_trends}</div>}
      {(va.significant_volume_changes || []).map((item,i) => (
        <div key={i} className="text-sm">
          {item.date}: {item.explanation}
        </div>
      ))}
      <hr className="my-1 border-gray-200" />

      <h6 className="text-sm font-semibold mt-1 mb-1">Indicator Correlations</h6>
      {ic.explanation && <div className="text-sm">{ic.explanation}</div>}
      <hr className="my-1 border-gray-200" />

      <h6 className="text-sm font-semibold mt-1 mb-1">Pivot Points</h6>
      {['daily','weekly','monthly'].map(ps => (
        <div key={ps}>
          <div className="text-xs font-semibold">{ps.toUpperCase()}</div>
          {(pp[ps] || []).map((p,i) => (
            <div key={i} className="text-sm">
              {p.date}: Pivot={p.pivot}, S1={p.support1}, R1={p.resistance1}
            </div>
          ))}
        </div>
      ))}
      <hr className="my-1 border-gray-200" />

      <h6 className="text-sm font-semibold mt-1 mb-1">Risk Management</h6>
      {(rm.rules || []).map((rule,i) => (
        <div key={i} className="text-sm">{rule}</div>
      ))}
      <hr className="my-1 border-gray-200" />

      <h6 className="text-sm font-semibold mt-1 mb-1">Feedback</h6>
      {fb.note && <div className="text-sm">{fb.note}</div>}
      {fb.suggestions && <div className="text-sm">{fb.suggestions}</div>}
      </div>
    </motion.div>
  );
}

InsightsPanel.propTypes = {
  analysis: PropTypes.object.isRequired,
};
