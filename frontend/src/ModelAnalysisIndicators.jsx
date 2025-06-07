import React from 'react';
import IndicatorGroup from './IndicatorGroup';
import { modelAnalysisIndicators } from './indicatorGroups';

export default function ModelAnalysisIndicators({ available, layers, toggleLayer }) {
  // Всегда показываем список modelAnalysisIndicators, не фильтруя по `available`
  const indicators = modelAnalysisIndicators;
  return (
    <IndicatorGroup
      title="Модельный анализ"
      indicators={indicators}
      layers={layers}
      toggleLayer={toggleLayer}
    />
  );
}
