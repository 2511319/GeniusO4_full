import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import React from 'react';
import { describe, it, expect } from 'vitest';
import CommentsPanel from './CommentsPanel';

describe('CommentsPanel', () => {
  it('renders layer explanations', () => {
    const analysis = {
      primary_analysis: {},
      trend_lines: { explanation: 'Trend lines info' },
      divergence_analysis: { explanation: 'Divergence details' }
    };
    const layers = ['trend_lines', 'divergence_analysis'];
    render(<CommentsPanel analysis={analysis} layers={layers} />);

    fireEvent.click(screen.getByRole('tab', { name: /Explanation/i }));

    expect(screen.getByText('trend_lines')).toBeInTheDocument();
    expect(screen.getByText('Trend lines info')).toBeInTheDocument();
    expect(screen.getByText('divergence_analysis')).toBeInTheDocument();
    expect(screen.getByText('Divergence details')).toBeInTheDocument();
  });
});
