import { render, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import TradingViewChart from './TradingViewChart';

const mockAddLineSeries = vi.fn(() => ({ setData: vi.fn() }));
const mockAddHistogramSeries = vi.fn(() => ({ setData: vi.fn() }));
const mockAddCandlestickSeries = vi.fn(() => ({ setData: vi.fn() }));
const mockSubscribeVisibleTimeRangeChange = vi.fn();
const mockSubscribeVisibleLogicalRangeChange = vi.fn();
const mockSubscribeCrosshairMove = vi.fn();

vi.mock('lightweight-charts', () => {
  return {
    createChart: vi.fn(() => ({
      addLineSeries: mockAddLineSeries,
      addHistogramSeries: mockAddHistogramSeries,
      addCandlestickSeries: mockAddCandlestickSeries,
      timeScale: () => ({
        subscribeVisibleTimeRangeChange: mockSubscribeVisibleTimeRangeChange,
        subscribeVisibleLogicalRangeChange: mockSubscribeVisibleLogicalRangeChange,
        setVisibleRange: vi.fn(),
        setVisibleLogicalRange: vi.fn(),
        unsubscribeVisibleTimeRangeChange: vi.fn(),
        unsubscribeVisibleLogicalRangeChange: vi.fn()
      }),
      subscribeCrosshairMove: mockSubscribeCrosshairMove,
      unsubscribeCrosshairMove: vi.fn(),
      setCrosshairPosition: vi.fn(),
      clearCrosshairPosition: vi.fn(),
      applyOptions: vi.fn(),
      remove: vi.fn()
    }))
  };
});

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

  it('creates line series for panel indicator', async () => {
    const data = [{ 'Open Time': '2021-01-01', Open: 1, High: 1, Low: 1, Close: 1, RSI: 50 }];
    render(<TradingViewChart data={data} layers={['RSI']} />);
    await waitFor(() => expect(mockAddLineSeries).toHaveBeenCalled());
  });

  it('subscribes to time range changes for synchronization', async () => {
    const data = [{ 'Open Time': '2021-01-01', Open: 1, High: 1, Low: 1, Close: 1, RSI: 50 }];
    render(<TradingViewChart data={data} layers={['RSI']} />);
    await waitFor(() => expect(mockSubscribeVisibleTimeRangeChange).toHaveBeenCalled());
    await waitFor(() => expect(mockSubscribeCrosshairMove).toHaveBeenCalled());
  });
});
