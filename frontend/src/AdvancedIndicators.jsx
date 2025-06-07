import React from 'react';
import IndicatorGroup from './IndicatorGroup';
import { advancedIndicators } from './indicatorGroups';

export default function AdvancedIndicators({ available, layers, toggleLayer }) {
  // advancedIndicators не зависят от полученных колонок данных,
  // поэтому показываем все доступные слои, игнорируя список `available`
  const indicators = advancedIndicators;
  return (
    <IndicatorGroup
      title="Продвинутые"
      indicators={indicators}
      layers={layers}
      toggleLayer={toggleLayer}
    />
  );
}
