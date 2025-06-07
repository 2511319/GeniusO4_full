import { render, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import TradingViewChart from './TradingViewChart';

const mockCreateRay = vi.fn();
const mockAddLineSeries = vi.fn(() => ({ setData: vi.fn() }));
const mockAddCandlestickSeries = vi.fn(() => ({ setData: vi.fn(), createRay: mockCreateRay }));
const mockSubscribeCrosshairMove = vi.fn();
const mockFitContent = vi.fn();

vi.mock('lightweight-charts', () => ({
  createChart: vi.fn(() => ({
    addCandlestickSeries: mockAddCandlestickSeries,
    addLineSeries: mockAddLineSeries,
    subscribeCrosshairMove: mockSubscribeCrosshairMove,
    removeSeries: vi.fn(),
    resize: vi.fn(),
    timeScale: () => ({ fitContent: mockFitContent }),
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
    render(<TradingViewChart data={data} layers={[]} showSR />);
    await waitFor(() => expect(mockCreateRay).toHaveBeenCalled());
  });

  it('renders indicator line series', async () => {
    const data = [{ time: 1, open: 1, high: 2, low: 0, close: 1, RSI: 70 }];
    render(<TradingViewChart data={data} layers={['RSI']} />);
    await waitFor(() => expect(mockAddLineSeries).toHaveBeenCalled());
  });

  it('fits time scale to content', async () => {
    const data = [{ time: 1, open: 1, high: 2, low: 0, close: 1 }];
    render(<TradingViewChart data={data} layers={[]} />);
    await waitFor(() => expect(mockFitContent).toHaveBeenCalled());
  });
});
