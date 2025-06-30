import React from 'react';
import IndicatorGroup from './IndicatorGroup';
import { technicalIndicators, indicatorColumnMap } from './indicatorGroups';

export default function TechnicalIndicators({ available, layers, toggleLayer }) {
  const indicators = technicalIndicators.filter((name) => {
    const cols = indicatorColumnMap[name] || [name];
    return cols.every((c) => available.includes(c));
  });
  return (
    <IndicatorGroup
      title="Технические"
      indicators={indicators}
      layers={layers}
      toggleLayer={toggleLayer}
    />
  );
}
