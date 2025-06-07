import { render, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import TradingViewChart from './TradingViewChart';

const mockCreatePriceLine = vi.fn();
const mockAddCandlestickSeries = vi.fn(() => ({ setData: vi.fn(), createPriceLine: mockCreatePriceLine }));
const mockSubscribeCrosshairMove = vi.fn();

vi.mock('lightweight-charts', () => ({
  createChart: vi.fn(() => ({
    addCandlestickSeries: mockAddCandlestickSeries,
    subscribeCrosshairMove: mockSubscribeCrosshairMove,
    removeSeries: vi.fn(),
    resize: vi.fn(),
  })),
}));

describe('TradingViewChart', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('creates candlestick series with data', async () => {
    const data = [{ time: 1, open: 1, high: 2, low: 0, close: 1 }];
    render(<TradingViewChart data={data} layers={[]} />);
    await waitFor(() => expect(mockAddCandlestickSeries).toHaveBeenCalled());
  });

  it('adds horizontal lines for support/resistance', async () => {
    const data = Array.from({ length: 30 }).map((_, i) => ({
      time: i,
      open: 0,
      high: i,
      low: 0,
      close: 0
    }));
    render(<TradingViewChart data={data} layers={[]} />);
    await waitFor(() => expect(mockCreatePriceLine).toHaveBeenCalled());
  });
});
