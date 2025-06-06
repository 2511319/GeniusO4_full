import React from 'react';
import IndicatorGroup from './IndicatorGroup';
import { advancedIndicators } from './indicatorGroups';

export default function AdvancedIndicators({ available, layers, toggleLayer }) {
  const indicators = advancedIndicators.filter((i) => available.includes(i));
  return (
    <IndicatorGroup
      title="Продвинутые"
      indicators={indicators}
      layers={layers}
      toggleLayer={toggleLayer}
    />
  );
}
