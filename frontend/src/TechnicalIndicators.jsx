import React from 'react';
import IndicatorGroup from './IndicatorGroup';
import { technicalIndicators } from './indicatorGroups';

export default function TechnicalIndicators({ available, layers, toggleLayer }) {
  const indicators = technicalIndicators.filter((i) => available.includes(i));
  return (
    <IndicatorGroup
      title="Технические"
      indicators={indicators}
      layers={layers}
      toggleLayer={toggleLayer}
    />
  );
}
