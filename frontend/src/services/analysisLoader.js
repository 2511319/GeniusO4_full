import fs from 'fs';
import path from 'path';

export function parseAnalysis(content) {
  try {
    return JSON.parse(content);
  } catch (err) {
    console.error('Invalid JSON', err);
    return null;
  }
}

export async function fetchAnalysis(dir = path.join(process.cwd(), '..', 'api', 'dev_logs')) {
  try {
    const files = fs
      .readdirSync(dir)
      .filter((f) => f.startsWith('chatgpt_response_') && f.endsWith('.json'))
      .sort();
    if (!files.length) return null;
    const file = path.join(dir, files[files.length - 1]);
    const data = fs.readFileSync(file, 'utf-8');
    return parseAnalysis(data);
  } catch (err) {
    console.error('Failed to read analysis', err);
    return null;
  }
}
