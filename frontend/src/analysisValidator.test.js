import { describe, it, expect, vi } from 'vitest';
import { validateAnalysis } from './analysisValidator';

describe('validateAnalysis unfinished_zones', () => {
  it('warns when coordinates missing', () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    validateAnalysis({
      unfinished_zones: [{ type: 'a', level: 1, date: 'd' }]
    });
    expect(warn).toHaveBeenCalledWith('Нехватка координат для unfinished_zones');
    warn.mockRestore();
  });

  it('does not warn when coordinates present', () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    validateAnalysis({
      unfinished_zones: [{
        type: 'a',
        level: 1,
        date: 'd',
        start_point: { x: 1, y: 2 },
        end_point: { x: 2, y: 3 }
      }]
    });
    expect(warn).not.toHaveBeenCalled();
    warn.mockRestore();
  });
});

describe('validateAnalysis gap_analysis', () => {
  it('warns when coordinates missing', () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    validateAnalysis({
      gap_analysis: { gaps: [{ date: 'd', price_range: [1, 2] }], comment: '' }
    });
    expect(warn).toHaveBeenCalledWith('Нехватка координат для gap_analysis');
    warn.mockRestore();
  });

  it('does not warn when coordinates present', () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    validateAnalysis({
      gap_analysis: {
        gaps: [{
          date: 'd',
          start_point: { x: 1, y: 2 },
          end_point: { x: 3, y: 4 }
        }],
        comment: ''
      }
    });
    expect(warn).not.toHaveBeenCalled();
    warn.mockRestore();
  });
});
