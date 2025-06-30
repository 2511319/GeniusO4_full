// frontend/src/utils/timeUtils.js

/**
 * Оптимизированные утилиты для работы с временными метками
 * Повышают производительность обработки больших объемов данных
 */

// Кэш для парсинга временных меток
const timestampCache = new Map();
const MAX_CACHE_SIZE = 10000;

// Константы для валидации
const MIN_TIMESTAMP = 946684800;   // 2000-01-01 00:00:00 UTC
const MAX_TIMESTAMP = 4102444800;  // 2100-01-01 00:00:00 UTC
const MS_THRESHOLD = 1e10;         // Порог для определения миллисекунд

/**
 * Очищает кэш если он становится слишком большим
 */
function cleanCache() {
  if (timestampCache.size > MAX_CACHE_SIZE) {
    // Удаляем половину самых старых записей
    const entries = Array.from(timestampCache.entries());
    const toDelete = entries.slice(0, Math.floor(entries.length / 2));
    toDelete.forEach(([key]) => timestampCache.delete(key));
  }
}

/**
 * Оптимизированная функция парсинга временных меток с кэшированием
 * @param {string|number|Date} d - временная метка в различных форматах
 * @returns {number|null} Unix timestamp в секундах или null при ошибке
 */
export function toUnix(d) {
  if (!d) return null;

  // Проверяем кэш для строковых значений
  const cacheKey = typeof d === 'string' ? d : null;
  if (cacheKey && timestampCache.has(cacheKey)) {
    return timestampCache.get(cacheKey);
  }

  try {
    let parsed;
    let timestamp;

    if (typeof d === 'number') {
      // Обработка числовых timestamp
      timestamp = d > MS_THRESHOLD ? Math.floor(d / 1000) : d;
    } else if (typeof d === 'string') {
      // Оптимизированная обработка строк
      if (d.includes('T') || d.includes(' ')) {
        // ISO формат или datetime строка
        parsed = new Date(d.includes('T') ? d : d.replace(' ', 'T') + 'Z');
      } else {
        // Простая дата
        parsed = new Date(d + 'T00:00:00Z');
      }
      
      if (isNaN(parsed.getTime())) {
        console.warn('Invalid date string:', d);
        return null;
      }
      
      timestamp = Math.floor(parsed.getTime() / 1000);
    } else if (d instanceof Date) {
      // Обработка Date объектов
      timestamp = Math.floor(d.getTime() / 1000);
    } else {
      // Попытка преобразования через Date конструктор
      parsed = new Date(d);
      if (isNaN(parsed.getTime())) {
        console.warn('Cannot parse timestamp:', d);
        return null;
      }
      timestamp = Math.floor(parsed.getTime() / 1000);
    }

    // Валидация разумных границ
    if (!timestamp || Number.isNaN(timestamp) || timestamp < MIN_TIMESTAMP || timestamp > MAX_TIMESTAMP) {
      console.warn('Invalid or unreasonable timestamp:', d, 'parsed to:', timestamp);
      return null;
    }

    // Кэшируем результат для строковых ключей
    if (cacheKey) {
      timestampCache.set(cacheKey, timestamp);
      cleanCache();
    }

    return timestamp;
  } catch (error) {
    console.warn('Error parsing timestamp:', d, error);
    return null;
  }
}

/**
 * Пакетная обработка временных меток для лучшей производительности
 * @param {Array} timestamps - массив временных меток
 * @returns {Array} массив Unix timestamps
 */
export function batchToUnix(timestamps) {
  if (!Array.isArray(timestamps)) {
    return [];
  }

  const results = new Array(timestamps.length);
  
  for (let i = 0; i < timestamps.length; i++) {
    results[i] = toUnix(timestamps[i]);
  }
  
  return results;
}

/**
 * Оптимизированная функция построения данных для серий графика
 * @param {Array} data - массив данных
 * @param {string} timeField - поле с временной меткой
 * @param {string} valueField - поле со значением
 * @returns {Array} отфильтрованные и отсортированные данные
 */
export function buildSeriesData(data, timeField = 'Open Time', valueField) {
  if (!Array.isArray(data) || !valueField) {
    return [];
  }

  const seen = new Set();
  const results = [];
  
  // Предварительно парсим все временные метки
  const timestamps = data.map(item => toUnix(item[timeField]));
  
  for (let i = 0; i < data.length; i++) {
    const time = timestamps[i];
    const value = data[i][valueField];
    
    if (time === null || value === undefined || value === null) {
      continue;
    }
    
    // Проверяем дубликаты
    if (seen.has(time)) {
      continue;
    }
    
    seen.add(time);
    results.push({ time, value });
  }
  
  // Сортируем по времени
  results.sort((a, b) => a.time - b.time);
  
  return results;
}

/**
 * Оптимизированная функция построения данных для свечного графика
 * @param {Array} data - массив OHLC данных
 * @param {string} timeField - поле с временной меткой
 * @returns {Array} отфильтрованные и отсортированные свечные данные
 */
export function buildCandleData(data, timeField = 'Open Time') {
  if (!Array.isArray(data)) {
    return [];
  }

  const seen = new Set();
  const results = [];
  
  // Предварительно парсим все временные метки
  const timestamps = data.map(item => toUnix(item[timeField]));
  
  for (let i = 0; i < data.length; i++) {
    const time = timestamps[i];
    const candle = data[i];
    
    if (time === null || !candle.Open || !candle.High || !candle.Low || !candle.Close) {
      continue;
    }
    
    // Проверяем дубликаты
    if (seen.has(time)) {
      continue;
    }
    
    seen.add(time);
    results.push({
      time,
      open: candle.Open,
      high: candle.High,
      low: candle.Low,
      close: candle.Close
    });
  }
  
  // Сортируем по времени
  results.sort((a, b) => a.time - b.time);
  
  return results;
}

/**
 * Валидирует временной диапазон
 * @param {*} start - начальная временная метка
 * @param {*} end - конечная временная метка
 * @returns {Object|null} объект с валидированными временными метками или null
 */
export function validateTimeRange(start, end) {
  const startTime = toUnix(start);
  const endTime = toUnix(end);
  
  if (!startTime || !endTime) {
    return null;
  }
  
  if (startTime >= endTime) {
    console.warn('Start time must be before end time:', start, end);
    return null;
  }
  
  return { start: startTime, end: endTime };
}

/**
 * Форматирует Unix timestamp в читаемую строку
 * @param {number} timestamp - Unix timestamp в секундах
 * @param {string} format - формат вывода ('date', 'datetime', 'time')
 * @returns {string} отформатированная строка
 */
export function formatTimestamp(timestamp, format = 'datetime') {
  if (!timestamp || typeof timestamp !== 'number') {
    return '';
  }
  
  try {
    const date = new Date(timestamp * 1000);
    
    switch (format) {
      case 'date':
        return date.toISOString().split('T')[0];
      case 'time':
        return date.toISOString().split('T')[1].split('.')[0];
      case 'datetime':
      default:
        return date.toISOString().replace('T', ' ').split('.')[0];
    }
  } catch (error) {
    console.warn('Error formatting timestamp:', timestamp, error);
    return '';
  }
}

/**
 * Очищает кэш временных меток (для тестирования или освобождения памяти)
 */
export function clearTimestampCache() {
  timestampCache.clear();
}

/**
 * Получает статистику кэша (для отладки)
 */
export function getCacheStats() {
  return {
    size: timestampCache.size,
    maxSize: MAX_CACHE_SIZE
  };
}
