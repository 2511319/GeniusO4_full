import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createBasicChart } from './chartUtils';
import { createChart } from 'lightweight-charts';

vi.mock('lightweight-charts', () => ({
  createChart: vi.fn(() => ({}))
}));

describe('createBasicChart', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('uses default options', () => {
    const div = document.createElement('div');
    createBasicChart(div, 200, 100);
    const opts = createChart.mock.calls[0][1];
    expect(opts.layout).toEqual({ backgroundColor: '#fff', textColor: '#000' });
    expect(opts.grid).toEqual({ vertLines: { visible: false }, horzLines: { color: '#eee' } });
  });

  it('merges provided options', () => {
    const div = document.createElement('div');
    createBasicChart(div, 100, 50, { layout: { backgroundColor: '#111' }, crosshair: { mode: 1 } });
    const opts = createChart.mock.calls[0][1];
    expect(opts.layout).toEqual({ backgroundColor: '#111', textColor: '#000' });
    expect(opts.crosshair).toEqual({ mode: 1 });
  });
});
