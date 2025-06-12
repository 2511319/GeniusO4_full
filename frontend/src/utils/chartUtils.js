// src/utils/chartUtils.js

/**
 * Heikin-Ashi candles
 * @param {Array<{time, open, high, low, close}>} candles
 * @returns {Array<{time, open, high, low, close}>}
 */
export function computeHeikinAshi(candles) {
  if (!candles?.length) return [];
  const ha = [];
  candles.forEach((c, idx) => {
    const closeHA = (c.open + c.high + c.low + c.close) / 4;
    let openHA;
    if (idx === 0) {
      openHA = (c.open + c.close) / 2;
    } else {
      const prev = ha[idx - 1];
      openHA = (prev.open + prev.close) / 2;
    }
    const highHA = Math.max(c.high, openHA, closeHA);
    const lowHA  = Math.min(c.low, openHA, closeHA);
    ha.push({ time: c.time, open: openHA, high: highHA, low: lowHA, close: closeHA });
  });
  return ha;
}

/**
 * Очень упрощённый Renko-алгоритм: размер кирпича = avgATR × factor (default 2).
 * @param {Array<{time, open, high, low, close}>} candles
 * @param {string} resolution      // '1m','1h','1d' — пока не используется
 * @param {number} factor          // multiplier to ATR
 * @returns {Array<{time, open, high, low, close}>}
 */
export function computeRenko(candles, resolution, factor = 2) {
  if (!candles?.length) return [];

  // расчёт среднего ATR за последние 14 свечей
  const atr14 =
    candles
      .slice(-15)
      .reduce(
        (s, c, i, arr) =>
          i === 0 ? 0 : s + Math.max(c.high - c.low, Math.abs(c.high - arr[i - 1].close), Math.abs(c.low - arr[i - 1].close)),
        0
      ) / 14 || 1;

  const brick = atr14 * factor;

  const renko = [];
  let lastClose = candles[0].close;
  candles.forEach((c) => {
    while (Math.abs(c.close - lastClose) >= brick) {
      const direction = c.close > lastClose ? 1 : -1;
      const newClose  = lastClose + direction * brick;
      renko.push({
        time: c.time,
        open: lastClose,
        close: newClose,
        high: Math.max(lastClose, newClose),
        low: Math.min(lastClose, newClose),
      });
      lastClose = newClose;
    }
  });
  return renko;
}

/* ==================================================================== */
/* Заглушки-детекторы — чтоб импорт существовал (можно доработать позже) */
/* ==================================================================== */

/**
 * Находит простые уровни поддержки/сопротивления
 * @param {Array<{time, close}>} candles
 * @returns {Array<{level:number,count:number}>}
 */
export function findSRLevels(candles) {
  if (!candles?.length) return [];
  const levels = {};
  candles.forEach((c) => {
    const rounded = Math.round(c.close / 10) * 10; // округляем до «десятки»
    levels[rounded] = (levels[rounded] || 0) + 1;
  });
  return Object.entries(levels)
    .filter(([, cnt]) => cnt > 2)
    .map(([level, count]) => ({ level: Number(level), count }));
}

/**
 * Находит простые трендовые линии (по двум крайним экстремумам)
 * @param {Array<{time, high, low}>} candles
 * @returns {Array<{start_point:{date,price},end_point:{date,price},type}>}
 */
export function findTrendLines(candles) {
  if (candles.length < 2) return [];
  const first = candles[0];
  const last  = candles[candles.length - 1];
  return [
    {
      start_point: { date: first.time, price: first.low },
      end_point:   { date: last.time,  price: last.low },
      type: 'ascending',
    },
    {
      start_point: { date: first.time, price: first.high },
      end_point:   { date: last.time,  price: last.high },
      type: 'descending',
    },
  ];
}
