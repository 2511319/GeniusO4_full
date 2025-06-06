import React from 'react';
import IndicatorGroup from './IndicatorGroup';
import { modelAnalysisIndicators } from './indicatorGroups';

export default function ModelAnalysisIndicators({ available, layers, toggleLayer }) {
  const indicators = modelAnalysisIndicators.filter((i) => available.includes(i));
  return (
    <IndicatorGroup
      title="Модельный анализ"
      indicators={indicators}
      layers={layers}
      toggleLayer={toggleLayer}
    />
  );
}
