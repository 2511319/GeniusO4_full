import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';
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
  it('reads last file', async () => {
    const dir = path.join(__dirname, '__tmp__');
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, 'chatgpt_response_1.json'), '{"a":1}');
    fs.writeFileSync(path.join(dir, 'chatgpt_response_2.json'), '{"b":2}');
    const data = await fetchAnalysis(dir);
    fs.rmSync(dir, { recursive: true, force: true });
    expect(data).toEqual({ b: 2 });
  });
});
