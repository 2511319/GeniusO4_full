import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { Provider } from 'react-redux';
import { store } from '../store';
import App from '../App';
import { describe, it, expect, vi } from 'vitest';
import React from 'react';

vi.mock('./TradingViewChartWrapper', () => ({ default: () => <div data-testid="chart" /> }));
vi.mock('axios', () => ({
  default: {
    post: vi.fn(() => Promise.resolve({ data: { ohlc: [], analysis: {} } })),
    get: vi.fn(() => Promise.resolve({ data: { ohlc: [] } })),
  }
}));

describe('App', () => {
  it('renders navigation and home page', () => {
    render(
      <Provider store={store}>
        <App />
      </Provider>
    );
    expect(screen.getByText(/ChartGenius/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Запустить анализ/i })).toBeInTheDocument();
  });
});
