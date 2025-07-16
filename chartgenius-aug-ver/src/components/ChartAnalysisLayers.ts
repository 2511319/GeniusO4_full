// Класс для управления аналитическими слоями на графике
import { IChartApi, ISeriesApi, LineStyle } from 'lightweight-charts';
import {
  SupportResistanceLevel,
  TrendLine,
  ImbalanceZone,
  UnfinishedZone,
  CandlestickPattern,
  Divergence,
  ElliottWave,
  VirtualCandle,
  TradingStrategy,
  toTimestamp,
  sortAndDeduplicateData,
  COLORS,
  getTrendLineColor,
  getCandlestickPatternColor,
  getLineStyle,
} from '../utils/chartAnalysisUtils';

export class ChartAnalysisLayers {
  private chart: IChartApi;
  private candlestickSeries: ISeriesApi<"Candlestick">;
  private layers: Map<string, any[]> = new Map();

  constructor(chart: IChartApi, candlestickSeries: ISeriesApi<"Candlestick">) {
    this.chart = chart;
    this.candlestickSeries = candlestickSeries;
  }

  // Очистка всех слоев
  clearAllLayers() {
    this.layers.forEach((layerItems) => {
      layerItems.forEach((item) => {
        if (item && typeof item.remove === 'function') {
          item.remove();
        }
      });
    });
    this.layers.clear();
  }

  // Очистка конкретного слоя
  clearLayer(layerName: string) {
    const layerItems = this.layers.get(layerName);
    if (layerItems) {
      layerItems.forEach((item, index) => {
        if (item) {
          try {
            // Детальная диагностика типа элемента
            const itemType = item.constructor?.name || 'Unknown';
            const hasRemove = typeof item.remove === 'function';

            console.log(`Удаляем элемент ${index} в слое ${layerName}: тип=${itemType}, hasRemove=${hasRemove}`);

            // 1. Для PriceLine используем removePriceLine на серии (ПРИОРИТЕТ)
            // PriceLine создается только в tradingRecommendations
            // fibonacci теперь использует AreaSeries + LineSeries, supportResistance использует LineSeries, unfinishedZones и imbalances используют AreaSeries
            if (layerName === 'tradingRecommendations') {
              this.candlestickSeries.removePriceLine(item);
              console.log(`✅ PriceLine ${index} в слое ${layerName} успешно удален через removePriceLine()`);
            }
            // 2. Для серий с методом remove() используем item.remove()
            else if (hasRemove) {
              item.remove();
              console.log(`✅ Элемент ${index} в слое ${layerName} успешно удален через remove()`);
            }
            // 3. Для SeriesApi без метода remove() используем chart.removeSeries()
            // Это основной случай для LineSeries, CandlestickSeries, HistogramSeries
            else if (itemType === 'SeriesApi' || itemType.includes('Series')) {
              this.chart.removeSeries(item);
              console.log(`✅ SeriesApi ${index} в слое ${layerName} успешно удален через chart.removeSeries()`);
            }
            // 4. Для всех остальных случаев пытаемся удалить через chart.removeSeries()
            else {
              // Большинство элементов TradingView - это серии, попробуем удалить их через chart
              this.chart.removeSeries(item);
              console.log(`✅ Элемент ${index} в слое ${layerName} (тип: ${itemType}) удален через chart.removeSeries()`);
            }
          } catch (error) {
            console.error(`❌ Ошибка при удалении элемента ${index} слоя ${layerName}:`, error);
            // Попробуем альтернативный способ удаления
            try {
              if (typeof item.remove === 'function') {
                item.remove();
                console.log(`✅ Элемент ${index} в слое ${layerName} удален альтернативным способом через remove()`);
              }
            } catch (secondError) {
              console.error(`❌ Альтернативный способ удаления также не сработал:`, secondError);
            }
          }
        }
      });

      // Специальная обработка для слоев с маркерами
      if (layerName === 'candlestickPatterns' || layerName === 'divergences' ||
          layerName === 'elliottWaves' || layerName === 'tradingRecommendations') {
        // Очищаем маркеры с основной серии свечей
        this.candlestickSeries.setMarkers([]);
        console.log(`✅ Маркеры для слоя ${layerName} очищены`);
      }

      this.layers.delete(layerName);
      console.log(`✅ Слой ${layerName} полностью очищен`);
    } else {
      console.log(`ℹ️ Слой ${layerName} не найден или уже пуст`);
    }
  }

  // Добавление уровней поддержки/сопротивления
  addSupportResistanceLevels(supports: SupportResistanceLevel[], resistances: SupportResistanceLevel[]) {
    this.clearLayer('supportResistance');
    const layerItems: any[] = [];

    // Получаем временной диапазон данных для создания лучей
    // Используем фиксированное время в будущем, если visibleRange недоступен
    const timeScale = this.chart.timeScale();
    const visibleRange = timeScale.getVisibleRange();
    const currentTime = Date.now() / 1000;
    const futureTime = currentTime + (365 * 24 * 60 * 60); // +1 год в будущее
    const lastDataTime = visibleRange?.to || futureTime;

    console.log(`📊 Создаем уровни поддержки/сопротивления. Supports: ${supports.length}, Resistances: ${resistances.length}`);

    // Добавляем уровни поддержки (лучи)
    supports.forEach((support, index) => {
      const startTime = toTimestamp(support.date);

      console.log(`🟢 Создаем поддержку ${index + 1}: уровень ${support.level}, дата ${support.date}, timestamp ${startTime}`);

      // Создаем линейную серию для луча поддержки
      const raySeries = this.chart.addLineSeries({
        color: COLORS.support,
        lineWidth: 2,
        lineStyle: LineStyle.Solid,
        title: `Поддержка ${support.level}`,
      });

      // Создаем данные для луча от startTime до конца видимого диапазона
      const rayData = [
        { time: startTime as any, value: support.level },
        { time: lastDataTime as any, value: support.level }
      ];

      raySeries.setData(rayData);
      layerItems.push(raySeries);
      console.log(`✅ Поддержка ${support.level} создана успешно`);
    });

    // Добавляем уровни сопротивления (лучи)
    resistances.forEach((resistance, index) => {
      const startTime = toTimestamp(resistance.date);

      console.log(`🔴 Создаем сопротивление ${index + 1}: уровень ${resistance.level}, дата ${resistance.date}, timestamp ${startTime}`);

      // Создаем линейную серию для луча сопротивления
      const raySeries = this.chart.addLineSeries({
        color: COLORS.resistance,
        lineWidth: 2,
        lineStyle: LineStyle.Solid,
        title: `Сопротивление ${resistance.level}`,
      });

      // Создаем данные для луча от startTime до конца видимого диапазона
      const rayData = [
        { time: startTime as any, value: resistance.level },
        { time: lastDataTime as any, value: resistance.level }
      ];

      raySeries.setData(rayData);
      layerItems.push(raySeries);
      console.log(`✅ Сопротивление ${resistance.level} создано успешно`);
    });

    this.layers.set('supportResistance', layerItems);
    console.log(`📊 Слой supportResistance создан с ${layerItems.length} элементами`);
  }

  // Добавление линий тренда
  addTrendLines(trendLines: TrendLine[]) {
    this.clearLayer('trendLines');
    const layerItems: any[] = [];

    trendLines.forEach((trendLine) => {
      const lineSeries = this.chart.addLineSeries({
        color: getTrendLineColor(trendLine.type),
        lineWidth: 2,
        lineStyle: LineStyle.Solid,
        title: `Тренд (${trendLine.type})`,
      });

      const lineData = [
        {
          time: toTimestamp(trendLine.start_point.date) as any,
          value: trendLine.start_point.price,
        },
        {
          time: toTimestamp(trendLine.end_point.date) as any,
          value: trendLine.end_point.price,
        },
      ];

      // Сортируем и дедуплицируем данные перед передачей в setData
      const sortedLineData = sortAndDeduplicateData(lineData);
      lineSeries.setData(sortedLineData);
      layerItems.push(lineSeries);
    });

    this.layers.set('trendLines', layerItems);
  }

  // Добавление уровней Фибоначчи
  addFibonacciLevels(fibonacciData: any) {
    this.clearLayer('fibonacci');
    const layerItems: any[] = [];

    console.log(`📊 Создаем уровни Фибоначчи (альтернативный подход - прямоугольные области). Данные:`, fibonacciData);

    // Обрабатываем локальный тренд - создаем прямоугольные области между уровнями
    if (fibonacciData.based_on_local_trend) {
      const localFib = fibonacciData.based_on_local_trend;
      console.log(`🟢 Создаем локальный Fibonacci Retracement. Область:`, localFib.start_point, 'до', localFib.end_point);

      // Определяем границы прямоугольной области
      const startTime = toTimestamp(localFib.start_point.date);
      const endTime = toTimestamp(localFib.end_point.date);

      console.log(`🟢 Границы локального прямоугольника: время ${startTime}-${endTime}`);

      // Сортируем уровни по цене для создания областей между ними
      const sortedLevels = Object.entries(localFib.levels).sort(([,a], [,b]) => (b as number) - (a as number));

      // Создаем полупрозрачные области между соседними уровнями Фибоначчи
      for (let i = 0; i < sortedLevels.length - 1; i++) {
        const [upperLevel, upperPrice] = sortedLevels[i];
        const [lowerLevel, lowerPrice] = sortedLevels[i + 1];

        console.log(`🟢 Создаем область между уровнями ${upperLevel} (${upperPrice}) и ${lowerLevel} (${lowerPrice})`);

        // Создаем область между двумя уровнями
        const fibArea = this.chart.addAreaSeries({
          topColor: COLORS.fibonacci + (i % 2 === 0 ? '15' : '10'), // Чередующаяся прозрачность
          bottomColor: COLORS.fibonacci + '05',
          lineColor: COLORS.fibonacci,
          lineWidth: 1,
          title: `Фиб Лок ${upperLevel}-${lowerLevel}`,
        });

        // Создаем данные для области между уровнями
        const areaData = [
          { time: startTime as any, value: upperPrice as number },
          { time: endTime as any, value: upperPrice as number },
          { time: endTime as any, value: lowerPrice as number },
          { time: startTime as any, value: lowerPrice as number },
        ];

        // Сортируем данные по времени для правильного отображения
        const sortedAreaData = areaData.sort((a, b) => a.time - b.time);

        fibArea.setData([
          { time: startTime as any, value: upperPrice as number },
          { time: endTime as any, value: upperPrice as number },
        ]);

        layerItems.push(fibArea);
        console.log(`✅ Область между уровнями ${upperLevel}-${lowerLevel} создана успешно`);
      }

      // Создаем границы прямоугольника
      const topBorder = this.chart.addLineSeries({
        color: COLORS.fibonacci,
        lineWidth: 2,
        lineStyle: LineStyle.Solid,
        title: `Фиб Лок Верх`,
      });

      const bottomBorder = this.chart.addLineSeries({
        color: COLORS.fibonacci,
        lineWidth: 2,
        lineStyle: LineStyle.Solid,
        title: `Фиб Лок Низ`,
      });

      const maxPrice = Math.max(...Object.values(localFib.levels) as number[]);
      const minPrice = Math.min(...Object.values(localFib.levels) as number[]);

      topBorder.setData([
        { time: startTime as any, value: maxPrice },
        { time: endTime as any, value: maxPrice },
      ]);

      bottomBorder.setData([
        { time: startTime as any, value: minPrice },
        { time: endTime as any, value: minPrice },
      ]);

      layerItems.push(topBorder, bottomBorder);
    }

    // Обрабатываем глобальный тренд - создаем прямоугольные области между уровнями
    if (fibonacciData.based_on_global_trend) {
      const globalFib = fibonacciData.based_on_global_trend;
      console.log(`🔵 Создаем глобальный Fibonacci Retracement. Область:`, globalFib.start_point, 'до', globalFib.end_point);

      // Определяем границы прямоугольной области
      const startTime = toTimestamp(globalFib.start_point.date);
      const endTime = toTimestamp(globalFib.end_point.date);

      console.log(`🔵 Границы глобального прямоугольника: время ${startTime}-${endTime}`);

      // Сортируем уровни по цене для создания областей между ними
      const sortedLevels = Object.entries(globalFib.levels).sort(([,a], [,b]) => (b as number) - (a as number));

      // Создаем полупрозрачные области между соседними уровнями Фибоначчи
      for (let i = 0; i < sortedLevels.length - 1; i++) {
        const [upperLevel, upperPrice] = sortedLevels[i];
        const [lowerLevel, lowerPrice] = sortedLevels[i + 1];

        console.log(`🔵 Создаем область между уровнями ${upperLevel} (${upperPrice}) и ${lowerLevel} (${lowerPrice})`);

        // Создаем область между двумя уровнями
        const fibArea = this.chart.addAreaSeries({
          topColor: COLORS.fibonacciGlobal + (i % 2 === 0 ? '15' : '10'), // Чередующаяся прозрачность
          bottomColor: COLORS.fibonacciGlobal + '05',
          lineColor: COLORS.fibonacciGlobal,
          lineWidth: 1,
          title: `Фиб Глоб ${upperLevel}-${lowerLevel}`,
        });

        // Создаем данные для области между уровнями
        fibArea.setData([
          { time: startTime as any, value: upperPrice as number },
          { time: endTime as any, value: upperPrice as number },
        ]);

        layerItems.push(fibArea);
        console.log(`✅ Область между уровнями ${upperLevel}-${lowerLevel} создана успешно`);
      }

      // Создаем границы прямоугольника
      const topBorder = this.chart.addLineSeries({
        color: COLORS.fibonacciGlobal,
        lineWidth: 2,
        lineStyle: LineStyle.Solid,
        title: `Фиб Глоб Верх`,
      });

      const bottomBorder = this.chart.addLineSeries({
        color: COLORS.fibonacciGlobal,
        lineWidth: 2,
        lineStyle: LineStyle.Solid,
        title: `Фиб Глоб Низ`,
      });

      const maxPrice = Math.max(...Object.values(globalFib.levels) as number[]);
      const minPrice = Math.min(...Object.values(globalFib.levels) as number[]);

      topBorder.setData([
        { time: startTime as any, value: maxPrice },
        { time: endTime as any, value: maxPrice },
      ]);

      bottomBorder.setData([
        { time: startTime as any, value: minPrice },
        { time: endTime as any, value: minPrice },
      ]);

      layerItems.push(topBorder, bottomBorder);
    }

    this.layers.set('fibonacci', layerItems);
    console.log(`📊 Слой fibonacci создан с ${layerItems.length} элементами (альтернативный подход - области между уровнями)`);
  }

  // Добавление зон дисбаланса (полупрозрачные прямоугольники)
  addImbalanceZones(imbalances: ImbalanceZone[]) {
    this.clearLayer('imbalances');
    const layerItems: any[] = [];

    console.log(`📊 Создаем зоны дисбаланса. Количество: ${imbalances.length}`);

    imbalances.forEach((imbalance, index) => {
      console.log(`🔵 Создаем зону дисбаланса ${index + 1}:`, imbalance);

      // Создаем полупрозрачную область для зоны дисбаланса
      const areaSeries = this.chart.addAreaSeries({
        topColor: COLORS.imbalance + '40', // 25% прозрачность
        bottomColor: COLORS.imbalance + '10', // 6% прозрачность
        lineColor: COLORS.imbalance,
        lineWidth: 1,
        title: `Дисбаланс (${imbalance.type})`,
      });

      // Определяем границы прямоугольника
      const startTime = toTimestamp(imbalance.start_point.date);
      const endTime = toTimestamp(imbalance.end_point.date);
      const topPrice = Math.max(imbalance.start_point.price, imbalance.end_point.price);
      const bottomPrice = Math.min(imbalance.start_point.price, imbalance.end_point.price);

      console.log(`🔵 Параметры зоны: от ${startTime} (${topPrice}) до ${endTime} (${bottomPrice})`);

      // Создаем данные для полупрозрачной области
      const areaData = [
        { time: startTime as any, value: topPrice },
        { time: endTime as any, value: topPrice },
      ];

      areaSeries.setData(areaData);
      layerItems.push(areaSeries);
      console.log(`✅ Зона дисбаланса ${imbalance.type} создана успешно`);
    });

    this.layers.set('imbalances', layerItems);
    console.log(`📊 Слой imbalances создан с ${layerItems.length} элементами`);
  }

  // Добавление незавершенных зон (полупрозрачные прямоугольники)
  addUnfinishedZones(unfinishedZones: UnfinishedZone[]) {
    this.clearLayer('unfinishedZones');
    const layerItems: any[] = [];

    console.log(`📊 Создаем незавершенные зоны. Количество: ${unfinishedZones.length}`);

    // Получаем временной диапазон для создания зон
    const timeScale = this.chart.timeScale();
    const visibleRange = timeScale.getVisibleRange();
    const currentTime = Date.now() / 1000;
    const futureTime = currentTime + (365 * 24 * 60 * 60); // +1 год в будущее
    const endTime = visibleRange?.to || futureTime;

    unfinishedZones.forEach((zone, index) => {
      console.log(`🟠 Создаем незавершенную зону ${index + 1}:`, zone);

      // Создаем полупрозрачную область для незавершенной зоны
      const areaSeries = this.chart.addAreaSeries({
        topColor: COLORS.unfinished + '40', // 25% прозрачность
        bottomColor: COLORS.unfinished + '10', // 6% прозрачность
        lineColor: zone.line_color || COLORS.unfinished,
        lineWidth: 2,
        title: `${zone.type} (${zone.level})`,
      });

      // Определяем границы зоны
      const startTime = toTimestamp(zone.date);
      const zoneHeight = zone.level * 0.001; // Высота зоны (0.1% от уровня)
      const topPrice = zone.level + zoneHeight;
      const bottomPrice = zone.level - zoneHeight;

      console.log(`🟠 Параметры зоны: от ${startTime} до ${endTime}, уровень ${zone.level} (${bottomPrice}-${topPrice})`);

      // Создаем данные для полупрозрачной области
      const areaData = [
        { time: startTime as any, value: topPrice },
        { time: endTime as any, value: topPrice },
      ];

      areaSeries.setData(areaData);
      layerItems.push(areaSeries);
      console.log(`✅ Незавершенная зона ${zone.type} создана успешно`);
    });

    this.layers.set('unfinishedZones', layerItems);
    console.log(`📊 Слой unfinishedZones создан с ${layerItems.length} элементами`);
  }

  // Добавление свечных паттернов (маркеры)
  addCandlestickPatterns(patterns: CandlestickPattern[]) {
    this.clearLayer('candlestickPatterns');
    const layerItems: any[] = [];

    patterns.forEach((pattern) => {
      const markerSeries = this.chart.addLineSeries({
        color: getCandlestickPatternColor(pattern.type),
        lineWidth: 1,
        title: `Паттерн: ${pattern.type}`,
      });

      // Добавляем маркер
      const markers = [{
        time: toTimestamp(pattern.date) as any,
        position: pattern.type.includes('медвеж') || pattern.type.includes('bearish') ? 'aboveBar' as const : 'belowBar' as const,
        color: getCandlestickPatternColor(pattern.type),
        shape: pattern.type.includes('медвеж') || pattern.type.includes('bearish') ? 'arrowDown' as const : 'arrowUp' as const,
        text: pattern.type.substring(0, 3),
      }];

      this.candlestickSeries.setMarkers(markers);
      layerItems.push(markerSeries);
    });

    this.layers.set('candlestickPatterns', layerItems);
  }

  // Добавление дивергенций (маркеры)
  addDivergences(divergences: Divergence[]) {
    this.clearLayer('divergences');
    const layerItems: any[] = [];

    divergences.forEach((divergence) => {
      const markerSeries = this.chart.addLineSeries({
        color: COLORS.divergence,
        lineWidth: 1,
        title: `Дивергенция: ${divergence.indicator}`,
      });

      // Добавляем маркер дивергенции
      const markers = [{
        time: toTimestamp(divergence.date) as any,
        position: 'aboveBar' as const,
        color: COLORS.divergence,
        shape: 'circle' as const,
        text: 'D',
      }];

      this.candlestickSeries.setMarkers(markers);
      layerItems.push(markerSeries);
    });

    this.layers.set('divergences', layerItems);
  }

  // Добавление волн Эллиотта (соединенные отрезки с метками)
  addElliottWaves(elliottData: any) {
    this.clearLayer('elliottWaves');
    const layerItems: any[] = [];

    if (elliottData.waves) {
      elliottData.waves.forEach((wave: ElliottWave) => {
        // Создаем линию для каждой волны
        const waveSeries = this.chart.addLineSeries({
          color: COLORS.elliott,
          lineWidth: 2,
          lineStyle: LineStyle.Solid,
          title: `Волна ${wave.wave_number}`,
        });

        const waveData = [
          {
            time: toTimestamp(wave.start_point.date) as any,
            value: wave.start_point.price,
          },
          {
            time: toTimestamp(wave.end_point.date) as any,
            value: wave.end_point.price,
          },
        ];

        // Сортируем и дедуплицируем данные перед передачей в setData
        const sortedWaveData = sortAndDeduplicateData(waveData);
        waveSeries.setData(sortedWaveData);
        layerItems.push(waveSeries);

        // Добавляем маркер с номером волны в конечной точке
        const markers = [{
          time: toTimestamp(wave.end_point.date) as any,
          position: 'aboveBar' as const,
          color: COLORS.elliott,
          shape: 'circle' as const,
          text: wave.wave_number.toString(),
        }];

        this.candlestickSeries.setMarkers(markers);
      });
    }

    this.layers.set('elliottWaves', layerItems);
  }

  // Добавление визуального прогноза (полупрозрачные свечи)
  addPricePrediction(predictionData: any) {
    this.clearLayer('pricePrediction');
    const layerItems: any[] = [];

    if (predictionData.virtual_candles) {
      // Создаем серию для прогнозных свечей
      const predictionSeries = this.chart.addCandlestickSeries({
        upColor: 'rgba(38, 166, 154, 0.3)', // Полупрозрачный зеленый
        downColor: 'rgba(239, 83, 80, 0.3)', // Полупрозрачный красный
        borderVisible: true,
        wickUpColor: 'rgba(38, 166, 154, 0.5)',
        wickDownColor: 'rgba(239, 83, 80, 0.5)',
        borderUpColor: 'rgba(38, 166, 154, 0.7)',
        borderDownColor: 'rgba(239, 83, 80, 0.7)',
        title: 'Прогноз цены',
      });

      const predictionCandles = predictionData.virtual_candles.map((candle: VirtualCandle) => ({
        time: toTimestamp(candle.date) as any,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
      }));

      // Сортируем и дедуплицируем данные перед передачей в setData
      const sortedCandles = sortAndDeduplicateData(predictionCandles);
      predictionSeries.setData(sortedCandles);
      layerItems.push(predictionSeries);
    }

    this.layers.set('pricePrediction', layerItems);
  }

  // Добавление торговых рекомендаций (горизонтальные линии)
  addTradingRecommendations(strategies: TradingStrategy[]) {
    this.clearLayer('tradingRecommendations');
    const layerItems: any[] = [];

    strategies.forEach((strategy) => {
      // Линия входа
      const entryLine = this.candlestickSeries.createPriceLine({
        price: strategy.entry_point.Price,
        color: COLORS.entry,
        lineWidth: 2,
        lineStyle: LineStyle.Solid,
        axisLabelVisible: true,
        title: `Вход: ${strategy.entry_point.Price}`,
      });
      layerItems.push(entryLine);

      // Линия стоп-лосса
      const stopLossLine = this.candlestickSeries.createPriceLine({
        price: strategy.stop_loss,
        color: COLORS.stopLoss,
        lineWidth: 2,
        lineStyle: LineStyle.Dashed,
        axisLabelVisible: true,
        title: `Стоп: ${strategy.stop_loss}`,
      });
      layerItems.push(stopLossLine);

      // Линия тейк-профита
      const takeProfitLine = this.candlestickSeries.createPriceLine({
        price: strategy.take_profit,
        color: COLORS.takeProfit,
        lineWidth: 2,
        lineStyle: LineStyle.Dashed,
        axisLabelVisible: true,
        title: `Тейк: ${strategy.take_profit}`,
      });
      layerItems.push(takeProfitLine);
    });

    this.layers.set('tradingRecommendations', layerItems);
  }

  // Получение активных слоев
  getActiveLayers(): string[] {
    return Array.from(this.layers.keys());
  }
}
