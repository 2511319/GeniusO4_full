import { render, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import TradingViewChart from './TradingViewChart';

const mockAddLineSeries = vi.fn(() => ({ setData: vi.fn() }));
const mockAddHistogramSeries = vi.fn(() => ({ setData: vi.fn() }));
const mockAddCandlestickSeries = vi.fn(() => ({ setData: vi.fn() }));

vi.mock('lightweight-charts', () => ({
  createChart: vi.fn(() => ({
    addLineSeries: mockAddLineSeries,
    addHistogramSeries: mockAddHistogramSeries,
    addCandlestickSeries: mockAddCandlestickSeries
  }))
}));

describe('TradingViewChart', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('creates line series when indicator is selected', async () => {
    const data = [{ 'Open Time': '2021-01-01', Open: 1, High: 1, Low: 1, Close: 1, MA_20: 1 }];
    render(<TradingViewChart data={data} layers={['MA_20']} />);
    await waitFor(() => expect(mockAddLineSeries).toHaveBeenCalled());
  });

  it('creates histogram series for Volume', async () => {
    const data = [{ 'Open Time': '2021-01-01', Open: 1, High: 1, Low: 1, Close: 1, Volume: 5 }];
    render(<TradingViewChart data={data} layers={['Volume']} />);
    await waitFor(() => expect(mockAddHistogramSeries).toHaveBeenCalled());
  });
});
