import { describe, it, expect, vi } from 'vitest';
import { parseAnalysis, fetchAnalysis } from './analysisLoader';

const sample = '{"primary_analysis":{"global_trend":"up"}}';

describe('parseAnalysis', () => {
  it('parses valid json', () => {
    const obj = parseAnalysis(sample);
    expect(obj).toEqual({ primary_analysis: { global_trend: 'up' } });
  });

  it('returns null on invalid json', () => {
    const obj = parseAnalysis('{');
    expect(obj).toBeNull();
  });
});

describe('fetchAnalysis', () => {
  it('fetches data from url', async () => {
    const mockRes = { ok: true, text: () => Promise.resolve('{"b":2}') };
    const fetchSpy = vi.spyOn(global, 'fetch').mockResolvedValue(mockRes);
    const data = await fetchAnalysis('/api/test');
    expect(fetchSpy).toHaveBeenCalledWith('/api/test');
    expect(data).toEqual({ b: 2 });
    fetchSpy.mockRestore();
  });
});
