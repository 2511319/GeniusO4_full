
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
      out.push({ price: curH, type: 'resistance' });
    if (curL === Math.min(...lows))
      out.push({ price: curL, type: 'support' });
  }
  /* фильтр дублей ±0.1% */
  return out.reduce((acc, lvl) => {
    if (!acc.find((l) => Math.abs(l.price - lvl.price) / lvl.price < 0.001))
      acc.push(lvl);
    return acc;
  }, []);
}
