import { createChart } from 'lightweight-charts';


export function parseToUnix(dateString) {
  return Math.floor(new Date(dateString).getTime() / 1000);
}

export function computeHeikinAshi(raw) {
  if (!raw?.length) return [];
  const res = [];
  for (let i = 0; i < raw.length; i++) {
    const prev = res[i - 1] || raw[i];
    const cur  = raw[i];
    const close = (cur.open + cur.high + cur.low + cur.close) / 4;
    const open  = (prev.open + prev.close) / 2;
    const high  = Math.max(cur.high, open, close);
    const low   = Math.min(cur.low, open, close);
    res.push({ time: cur.time, open, high, low, close });
  }
  return res;
}

export function computeRenko(raw, brick = 0.5) {
  if (!raw?.length) return [];
  const res = [];
  let lastClose = raw[0].close;
  let lastTime  = raw[0].time;
  for (const c of raw) {
    const diff = c.close - lastClose;
    const bricks = Math.floor(Math.abs(diff) / brick);
    for (let i = 0; i < bricks; i++) {
      lastClose += Math.sign(diff) * brick;
      res.push({
        time: lastTime + i, // псевдо-время
        open: lastClose - Math.sign(diff) * brick,
        close: lastClose,
        high: Math.max(lastClose, lastClose - Math.sign(diff) * brick),
        low:  Math.min(lastClose, lastClose - Math.sign(diff) * brick),
      });
    }
    lastTime = c.time;
  }
  return res;
}

export function findSRLevels(data, depth = 14) {
  const out = [];
  for (let i = depth; i < data.length - depth; i++) {
    const slice = data.slice(i - depth, i + depth);
    const highs = slice.map((d) => d.high);
    const lows  = slice.map((d) => d.low);
    const curH  = data[i].high;
    const curL  = data[i].low;
    if (curH === Math.max(...highs))
      out.push({ price: curH, type: 'resistance', time: data[i].time });
    if (curL === Math.min(...lows))
      out.push({ price: curL, type: 'support', time: data[i].time });
  }
  /* фильтр дублей ±0.1% */
  return out.reduce((acc, lvl) => {
    if (!acc.find((l) => Math.abs(l.price - lvl.price) / lvl.price < 0.001))
      acc.push(lvl);
    return acc;
  }, []);
}

export function findTrendLines(data, minPoints = 3) {
  if (!Array.isArray(data) || data.length < minPoints) return [];
  const lines = [];

  const pushLine = (arr, type, start, end, key) => {
    if (end - start + 1 >= minPoints) {
      lines.push({
        type,
        from: { time: data[start].time, price: data[start][key] },
        to: { time: data[end].time, price: data[end][key] }
      });
    }
  };

  let startLow = 0;
  for (let i = 1; i < data.length; i++) {
    if (data[i].low > data[i - 1].low) continue;
    pushLine(lines, 'support', startLow, i - 1, 'low');
    startLow = i;
  }
  pushLine(lines, 'support', startLow, data.length - 1, 'low');

  let startHigh = 0;
  for (let i = 1; i < data.length; i++) {
    if (data[i].high < data[i - 1].high) continue;
    pushLine(lines, 'resistance', startHigh, i - 1, 'high');
    startHigh = i;
  }
  pushLine(lines, 'resistance', startHigh, data.length - 1, 'high');

  return lines;
}

export function parseOhlc(raw) {
  if (!Array.isArray(raw)) return [];
  return raw.map((d) => {
    const { 'Open Time': openTime, Open, High, Low, Close, ...rest } = d;
    return {
      time: parseToUnix(openTime),
      open: Number(Open),
      high: Number(High),
      low: Number(Low),
      close: Number(Close),
      ...rest,
    };
  });
}

export function parsePatterns(raw) {
  if (!Array.isArray(raw)) return [];
  return raw.map(({ date, price, type }) => ({
    time: parseToUnix(date),
    price: Number(price),
    type,
  }));
}

export function parseVirtualCandles(raw) {
  if (!Array.isArray(raw)) return [];
  return raw.map(({ date, open, high, low, close }) => ({
    time: parseToUnix(date),
    open: Number(open),
    high: Number(high),
    low: Number(low),
    close: Number(close)
  }));
}

export function createBasicChart(ref, width, height, opts = {}) {
  const { layout = {}, grid = {}, ...rest } = opts;
  return createChart(ref, {
    width,
    height,
    layout: {
      backgroundColor: '#fff',
      textColor: '#000',
      ...layout,
    },
    grid: {
      vertLines: { visible: false, ...(grid.vertLines || {}) },
      horzLines: { color: '#eee', ...(grid.horzLines || {}) },
      ...grid,
    },
    ...rest,
  });
}

