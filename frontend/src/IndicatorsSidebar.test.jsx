import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import IndicatorsSidebar from './IndicatorsSidebar';

describe('IndicatorsSidebar', () => {
  it('renders groups in correct order and handles toggles', () => {
    const toggleLayer = vi.fn();
    const setShowSR = vi.fn();
    const setShowTrends = vi.fn();

    render(
      <IndicatorsSidebar
        layers={[]}
        toggleLayer={toggleLayer}
        showSR={false}
        setShowSR={setShowSR}
        showTrends={false}
        setShowTrends={setShowTrends}
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
    expect(toggleLayer).toHaveBeenCalledWith('MA_20');

    fireEvent.click(screen.getByLabelText('Algo-SRlevel'));
    expect(setShowSR).toHaveBeenCalledWith(true);

    fireEvent.click(screen.getByLabelText('Trend lines'));
    expect(setShowTrends).toHaveBeenCalledWith(true);
  });
});
