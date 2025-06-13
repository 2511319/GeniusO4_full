import { describe, it, expect, vi } from 'vitest';
import { validateAnalysis } from './data/analysisValidator';

describe('validateAnalysis unfinished_zones', () => {
  it('warns when coordinates missing', () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    validateAnalysis({
      unfinished_zones: [{ type: 'a', level: 1, date: 'd', explanation: 'e' }]
    });
    expect(warn).toHaveBeenCalledWith('unfinished_zones[0] missing field: start_point');
    expect(warn).toHaveBeenCalledWith('unfinished_zones[0] missing field: end_point');
    warn.mockRestore();
  });

  it('does not warn when coordinates present', () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    validateAnalysis({
      unfinished_zones: [{
        type: 'a',
        level: 1,
        date: 'd',
        explanation: 'e',
        start_point: { x: 1, y: 2 },
        end_point: { x: 2, y: 3 }
      }]
    });
    const messages = warn.mock.calls.map(c => c[0]);
    expect(messages).not.toContain('unfinished_zones[0] missing field: start_point');
    expect(messages).not.toContain('unfinished_zones[0] missing field: end_point');
    warn.mockRestore();
  });
});

describe('validateAnalysis gap_analysis', () => {
  it('warns when coordinates missing', () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    validateAnalysis({
      gap_analysis: { gaps: [{ date: 'd', price_range: [1, 2] }], comment: '' }
    });
    expect(warn).toHaveBeenCalledWith('gap_analysis.gaps[0] missing start_point/end_point');
    expect(warn).toHaveBeenCalledWith('gap_analysis.gaps[0] missing explanation');
    warn.mockRestore();
  });

  it('does not warn when coordinates present', () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    validateAnalysis({
      gap_analysis: {
          gaps: [{
            date: 'd',
            start_point: { x: 1, y: 2 },
            end_point: { x: 3, y: 4 },
            explanation: 'e'
          }],
          comment: ''
        }
      });
    const messages = warn.mock.calls.map(c => c[0]);
    expect(messages).not.toContain('gap_analysis.gaps[0] missing start_point/end_point');
    expect(messages).not.toContain('gap_analysis.gaps[0] missing explanation');
    warn.mockRestore();
  });
});
