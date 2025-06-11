import { render, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import TradingViewChart from './TradingViewChart';

const mockCreateRay = vi.fn();
const mockAddLineSeries = vi.fn(() => ({ setData: vi.fn(), applyOptions: vi.fn() }));
const mockAddCandlestickSeries = vi.fn(() => ({ setData: vi.fn(), createRay: mockCreateRay, setMarkers: vi.fn(), applyOptions: vi.fn() }));
const mockSubscribeCrosshairMove = vi.fn();
const mockFitContent = vi.fn();

vi.mock('lightweight-charts', () => ({
  createChart: vi.fn(() => ({
    addCandlestickSeries: mockAddCandlestickSeries,
    addLineSeries: mockAddLineSeries,
    subscribeCrosshairMove: mockSubscribeCrosshairMove,
    unsubscribeCrosshairMove: vi.fn(),
    removeSeries: vi.fn(),
    resize: vi.fn(),
    timeScale: () => ({ fitContent: mockFitContent }),
  })),
}));

import { createChart } from 'lightweight-charts';

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

  it('draws trend lines when enabled', async () => {
    const data = [
      { time: 1, open: 0, high: 5, low: 1, close: 0 },
      { time: 2, open: 0, high: 4, low: 1.2, close: 0 },
      { time: 3, open: 0, high: 3, low: 1.4, close: 0 },
      { time: 4, open: 0, high: 2.5, low: 1.6, close: 0 }
    ];
    render(<TradingViewChart data={data} layers={[]} showTrends />);
    await waitFor(() => expect(mockCreateRay).toHaveBeenCalled());
  });

  it('renders indicator line series', async () => {
    const data = [{ time: 1, open: 1, high: 2, low: 0, close: 1, RSI: 70 }];
    render(<TradingViewChart data={data} layers={['RSI']} />);
    await waitFor(() => expect(mockAddLineSeries).toHaveBeenCalled());
  });

  it('shows candlestick pattern markers', async () => {
    const data = [{ time: 1, open: 1, high: 2, low: 0, close: 1 }];
    const patterns = [{ time: 1, price: 1, type: 'Doji' }];
    render(<TradingViewChart data={data} patterns={patterns} layers={['candlestick_patterns']} />);
    await waitFor(() => expect(mockAddCandlestickSeries.mock.results[0].value.setMarkers).toHaveBeenCalled());
  });

  it('fits time scale to content', async () => {
    const data = [{ time: 1, open: 1, high: 2, low: 0, close: 1 }];
    render(<TradingViewChart data={data} layers={[]} />);
    await waitFor(() => expect(mockFitContent).toHaveBeenCalled());
  });

  it('disables default tooltips', async () => {
    const data = [{ time: 1, open: 1, high: 2, low: 0, close: 1 }];
    render(<TradingViewChart data={data} layers={['RSI']} />);
    await waitFor(() => expect(createChart).toHaveBeenCalled());
    const options = createChart.mock.calls[0][1];
    expect(options.crosshair.vertLine.labelVisible).toBe(false);
    expect(options.crosshair.horzLine.labelVisible).toBe(false);
    expect(mockAddCandlestickSeries.mock.calls[0][0].crosshairMarkerVisible).toBe(false);
    expect(mockAddLineSeries.mock.calls[0][0].crosshairMarkerVisible).toBe(false);
  });

  it('renders forecast candlestick series', async () => {
    const data = [{ time: 1, open: 1, high: 2, low: 0, close: 1 }];
    const forecast = [{ time: 2, open: 1, high: 2, low: 0, close: 1 }];
    render(<TradingViewChart data={data} forecast={forecast} layers={['price_prediction']} />);
    await waitFor(() => expect(mockAddCandlestickSeries).toHaveBeenCalledTimes(2));
  });

  it('sets data for virtual candles', async () => {
    const data = [{ time: 1, open: 1, high: 2, low: 0, close: 1 }];
    const forecast = [{ time: 2, open: 1, high: 2, low: 0, close: 1 }];
    render(<TradingViewChart data={data} forecast={forecast} layers={['price_prediction']} />);
    await waitFor(() => expect(mockAddCandlestickSeries).toHaveBeenCalledTimes(2));
    const forecastSeries = mockAddCandlestickSeries.mock.results[1].value;
    expect(forecastSeries.setData).toHaveBeenCalledWith(forecast);
  });

  it('creates forecast series with ohlc format and opacity', async () => {
    const data = [{ time: 1, open: 1, high: 2, low: 0, close: 1 }];
    const forecast = [{ time: 2, open: 1, high: 2, low: 0, close: 1 }];
    render(<TradingViewChart data={data} forecast={forecast} layers={['price_prediction']} />);
    await waitFor(() => expect(mockAddCandlestickSeries).toHaveBeenCalledTimes(2));
    expect(mockAddCandlestickSeries.mock.calls[1][0]).toEqual({ priceFormat: { type: 'ohlc' } });
    const forecastSeries = mockAddCandlestickSeries.mock.results[1].value;
    expect(forecastSeries.applyOptions).toHaveBeenCalledWith({ opacity: 0.4 });
  });

  it('does not request tooltip data for disallowed layers', async () => {
    const data = [{ time: 1, open: 1, high: 2, low: 0, close: 1, RSI: 70 }];
    render(<TradingViewChart data={data} layers={['RSI']} />);
    await waitFor(() => expect(mockSubscribeCrosshairMove).toHaveBeenCalled());

    const handler = mockSubscribeCrosshairMove.mock.calls[0][0];
    const candleSeries = mockAddCandlestickSeries.mock.results[0].value;
    const lineSeries = mockAddLineSeries.mock.results[0].value;
    const get = vi.fn((s) => {
      if (s === candleSeries) return { value: { open: 1, high: 2, low: 0, close: 1 } };
      if (s === lineSeries) return { value: 70 };
    });

    handler({ time: 1, seriesData: { get, size: 2 }, point: { x: 0, y: 0 } });
    expect(get).toHaveBeenCalledWith(candleSeries);
    expect(get).not.toHaveBeenCalledWith(lineSeries);
  });

  it('requests tooltip data for allowed layers', async () => {
    const data = [{ time: 1, open: 1, high: 2, low: 0, close: 1, price_prediction: 1.1 }];
    render(<TradingViewChart data={data} layers={['price_prediction']} />);
    await waitFor(() => expect(mockSubscribeCrosshairMove).toHaveBeenCalled());

    const handler = mockSubscribeCrosshairMove.mock.calls[0][0];
    const candleSeries = mockAddCandlestickSeries.mock.results[0].value;
    const lineSeries = mockAddLineSeries.mock.results[0].value;
    const get = vi.fn((s) => {
      if (s === candleSeries) return { value: { open: 1, high: 2, low: 0, close: 1 } };
      if (s === lineSeries) return { value: 1.1 };
    });

    handler({ time: 1, seriesData: { get, size: 2 }, point: { x: 0, y: 0 } });
    expect(get).toHaveBeenCalledWith(candleSeries);
    expect(get).toHaveBeenCalledWith(lineSeries);
  });

  it('requests tooltip data for forecast candles', async () => {
    const data = [{ time: 1, open: 1, high: 2, low: 0, close: 1 }];
    const forecast = [{ time: 2, open: 1.1, high: 2.2, low: 0.9, close: 1.05 }];
    render(
      <TradingViewChart
        data={data}
        forecast={forecast}
        layers={['price_prediction']}
        analysis={{ price_prediction: { forecast: 'up' } }}
      />
    );
    await waitFor(() => expect(mockSubscribeCrosshairMove).toHaveBeenCalled());

    const handler = mockSubscribeCrosshairMove.mock.calls[0][0];
    const forecastSeries = mockAddCandlestickSeries.mock.results[1].value;
    const get = vi.fn(() => ({ value: { open: 1.1, high: 2.2, low: 0.9, close: 1.05 } }));
    const has = (s) => s === forecastSeries;

    handler({ time: 2, seriesData: { get, size: 1, has }, point: { x: 0, y: 0 } });
    expect(get).toHaveBeenCalledWith(forecastSeries);
  });

  it('toggles series visibility from legend', async () => {
    const data = [{ time: 1, open: 1, high: 2, low: 0, close: 1, RSI: 70 }];
    const applyOptions = vi.fn();
    mockAddLineSeries.mockReturnValueOnce({ setData: vi.fn(), applyOptions });
    const { findByText } = render(<TradingViewChart data={data} layers={['RSI']} />);
    const item = await findByText('RSI');
    item.click();
    expect(applyOptions).toHaveBeenCalledWith({ visible: false });
    item.click();
    expect(applyOptions).toHaveBeenLastCalledWith({ visible: true });
  });
});
