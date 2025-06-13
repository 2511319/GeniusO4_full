import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import React from 'react';
import { describe, it, expect } from 'vitest';
import CommentsPanel from './components/CommentsPanel';

describe('CommentsPanel', () => {
  it('renders layer explanations', () => {
    const analysis = {
      primary_analysis: {},
      trend_lines: { explanation: 'Trend lines info' },
      divergence_analysis: { explanation: 'Divergence details' }
    };
    const activeLayers = ['trend_lines', 'divergence_analysis'];
    render(<CommentsPanel analysis={analysis} activeLayers={activeLayers} />);

    fireEvent.click(screen.getByRole('tab', { name: /Explanation/i }));

    expect(screen.getByText('Trend Lines')).toBeInTheDocument();
    expect(screen.getByText('Trend lines info')).toBeInTheDocument();
    expect(screen.getByText('Divergence Analysis')).toBeInTheDocument();
    expect(screen.getByText('Divergence details')).toBeInTheDocument();
  });
});
