export function parseAnalysis(content) {
  try {
    return JSON.parse(content);
  } catch (err) {
    console.error('Invalid JSON', err);
    return null;
  }
}

export async function fetchAnalysis(url = '/api/testdata') {
  try {
    const res = await fetch(url);
    if (!res.ok) return null;
    const text = await res.text();
    return parseAnalysis(text);
  } catch (err) {
    console.error('Failed to load analysis', err);
    return null;
  }
}
