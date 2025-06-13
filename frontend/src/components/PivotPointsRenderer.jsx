// src/components/PivotPointsRenderer.jsx

import React, { useEffect } from 'react';
import PropTypes from 'prop-types';
import { parseToUnix } from '../utils/chartUtils';

/**
 * Отдельный компонент, подписывающийся на chartRef и рисующий
 * pivot_points (daily, weekly, monthly) на графике.
 * Предполагается, что chartRef и seriesStore прокинуты сверху.
 */
export default function PivotPointsRenderer({ chartRef, pivotPoints, onRegister }) {
  useEffect(() => {
    if (!chartRef.current || !pivotPoints) return;
    ['daily','weekly','monthly'].forEach(period => {
      const arr = pivotPoints[period] || [];
      arr.forEach((pt, idx) => {
        // Вертикальная линия
        const line = chartRef.current.addLineSeries({
          color: '#FFA500',
          lineWidth: 1,
          lineStyle: 3, // пунктир
        });
        line.setData([
          { time: parseToUnix(pt.date), value: pt.pivot },
          { time: parseToUnix(pt.date), value: pt.pivot + 0.0001 }, // небольшое смещение, чтобы линия отобразилась
        ]);
        // Маркер
        line.setMarkers([
          {
            time: parseToUnix(pt.date),
            position: 'belowBar',
            color: '#FFA500',
            shape: 'circle',
            text: 'P',
          }
        ]);
        onRegister(`pivot_${period}_${idx}`, line, '#FFA500', true, 'P');
      });
    });
  }, [chartRef, pivotPoints]);

  return null;
}

PivotPointsRenderer.propTypes = {
  chartRef:    PropTypes.object.isRequired,
  pivotPoints: PropTypes.object.isRequired,
  onRegister:  PropTypes.func.isRequired,
};
