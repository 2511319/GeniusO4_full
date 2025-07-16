// Утилиты для работы с аналитическими данными на графике

// Типы для аналитических элементов
export interface SupportResistanceLevel {
  level: number;
  date: string;
  explanation: string;
  ray_slope?: string;
}

export interface TrendLine {
  type: string;
  start_point: { date: string; price: number };
  end_point: { date: string; price: number };
  slope_angle?: string;
}

export interface FibonacciLevel {
  levels: { [key: string]: number };
  start_point: { date: string; price: number };
  end_point: { date: string; price: number };
  explanation: string;
}

export interface ImbalanceZone {
  type: string;
  start_point: { date: string; price: number };
  end_point: { date: string; price: number };
  price_range?: [number, number];
  explanation: string;
}

export interface UnfinishedZone {
  type: string;
  level: number;
  date: string;
  line_style?: string;
  line_color?: string;
  explanation: string;
}

export interface CandlestickPattern {
  date: string;
  type: string;
  price: number;
  explanation: string;
}

export interface Divergence {
  indicator: string;
  type: string;
  date: string;
  explanation: string;
}

export interface ElliottWave {
  wave_number: number;
  start_point: { date: string; price: number };
  end_point: { date: string; price: number };
}

export interface VirtualCandle {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
}

export interface TradingStrategy {
  strategy: string;
  entry_point: { Price: number; Date: string };
  exit_point?: { Price: number; Date: string };
  stop_loss: number;
  take_profit: number;
  risk?: string;
  profit?: string;
  other_details?: string;
}

// Утилитарные функции
export const toTimestamp = (dateString: string): number => {
  const timestamp = new Date(dateString).getTime() / 1000;
  return Math.floor(timestamp); // Убираем дробную часть для предотвращения дублирующихся временных меток
};

export const formatPrice = (price: number): string => {
  return price.toFixed(2);
};

// Функция для сортировки и дедупликации данных по времени
export const sortAndDeduplicateData = <T extends { time: any }>(data: T[]): T[] => {
  return data
    .sort((a, b) => Number(a.time) - Number(b.time))
    .filter((item, index, arr) =>
      index === 0 || Number(item.time) !== Number(arr[index - 1].time)
    );
};

// Цветовая схема для различных элементов
export const COLORS = {
  support: '#26A69A',      // Зеленый для поддержки
  resistance: '#EF5350',   // Красный для сопротивления
  trendUp: '#26A69A',      // Зеленый для восходящего тренда
  trendDown: '#EF5350',    // Красный для нисходящего тренда
  fibonacci: '#FFB74D',    // Оранжевый для локального Фибоначчи
  fibonacciGlobal: '#9C27B0', // Фиолетовый для глобального Фибоначчи
  imbalance: '#2196F3',    // Синий для зон дисбаланса
  unfinished: '#FF9800',   // Оранжевый для незавершенных зон
  bullishPattern: '#4CAF50', // Зеленый для бычьих паттернов
  bearishPattern: '#F44336', // Красный для медвежьих паттернов
  divergence: '#2196F3',   // Синий для дивергенций
  elliott: '#9E9E9E',      // Серый для волн Эллиотта
  prediction: '#607D8B',   // Серо-синий для прогноза
  entry: '#2196F3',        // Синий для входа
  stopLoss: '#F44336',     // Красный для стоп-лосса
  takeProfit: '#4CAF50',   // Зеленый для тейк-профита
};

// Стили линий
export const LINE_STYLES = {
  solid: 0,
  dotted: 1,
  dashed: 2,
  largeDashed: 3,
  sparseDotted: 4,
};

// Функция для получения цвета линии тренда на основе типа
export const getTrendLineColor = (type: string): string => {
  if (type.includes('восходящ') || type.includes('bullish') || type.includes('up')) {
    return COLORS.trendUp;
  } else if (type.includes('нисходящ') || type.includes('bearish') || type.includes('down')) {
    return COLORS.trendDown;
  }
  return COLORS.elliott; // По умолчанию серый
};

// Функция для получения цвета свечного паттерна
export const getCandlestickPatternColor = (type: string): string => {
  if (type.includes('бычь') || type.includes('bullish') || type.includes('bull')) {
    return COLORS.bullishPattern;
  } else if (type.includes('медвеж') || type.includes('bearish') || type.includes('bear')) {
    return COLORS.bearishPattern;
  }
  return COLORS.divergence; // По умолчанию синий
};

// Функция для получения стиля линии на основе строкового описания
export const getLineStyle = (styleString?: string): number => {
  if (!styleString) return LINE_STYLES.solid;
  
  if (styleString.includes('dashed')) return LINE_STYLES.dashed;
  if (styleString.includes('dotted')) return LINE_STYLES.dotted;
  
  return LINE_STYLES.solid;
};
