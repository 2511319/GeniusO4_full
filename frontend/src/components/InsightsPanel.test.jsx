import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import React from 'react';
import { describe, it, expect } from 'vitest';
import InsightsPanel from './InsightsPanel';

const sample = {
  indicators_analysis: { RSI: { trend: 'up' } },
  volume_analysis: { volume_trends: 'Increasing' },
  pivot_points: { daily: [{ date: '2020-01-01', pivot: 1, support1: 0.9, resistance1: 1.1 }] }
};

describe('InsightsPanel', () => {
  it('renders analysis sections', () => {
    render(<InsightsPanel analysis={sample} />);
    expect(screen.getByText('Indicators Analysis')).toBeInTheDocument();
    expect(screen.getByText('RSI')).toBeInTheDocument();
    expect(screen.getByText('trend: up')).toBeInTheDocument();
    expect(screen.getByText('Volume Analysis')).toBeInTheDocument();
    expect(screen.getByText('Increasing')).toBeInTheDocument();
    expect(screen.getByText('Pivot Points')).toBeInTheDocument();
    expect(screen.getByText('2020-01-01: Pivot=1, S1=0.9, R1=1.1')).toBeInTheDocument();
  });
});
