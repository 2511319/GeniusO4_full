import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import IndicatorsSidebar from './components/IndicatorsSidebar';

describe('IndicatorsSidebar', () => {
  it('renders groups in correct order and handles toggles', () => {
    const setActiveLayers = vi.fn();

    render(
      <IndicatorsSidebar
        activeLayers={[]}
        setActiveLayers={setActiveLayers}
      />
    );

    const titles = screen.getAllByRole('button').map((btn) => btn.textContent);
    expect(titles).toEqual([
      'Overlays',
      'Volume',
      'Momentum',
      'Volatility',
      'MACD',
      'Model Analysis',
      'Forecast'
    ]);

    fireEvent.click(screen.getByLabelText('MA_20'));
    expect(setActiveLayers).toHaveBeenCalled();
    const toggleMA = setActiveLayers.mock.calls[0][0];
    expect(toggleMA([])).toEqual(['MA_20']);

    fireEvent.click(screen.getByLabelText('trend_lines'));
    const toggleTrends = setActiveLayers.mock.calls[1][0];
    expect(toggleTrends([])).toEqual(['trend_lines']);
  });
});
