// Класс для управления стандартными техническими индикаторами на графике
import { IChartApi, ISeriesApi, LineStyle } from 'lightweight-charts';
import { toTimestamp } from '../utils/chartAnalysisUtils';

export class ChartIndicators {
  private chart: IChartApi;
  private candlestickSeries: ISeriesApi<"Candlestick">;
  private indicators: Map<string, any[]> = new Map();

  constructor(chart: IChartApi, candlestickSeries: ISeriesApi<"Candlestick">) {
    this.chart = chart;
    this.candlestickSeries = candlestickSeries;
  }

  // Очистка всех индикаторов
  clearAllIndicators() {
    this.indicators.forEach((indicatorItems) => {
      indicatorItems.forEach((item) => {
        if (item && typeof item.remove === 'function') {
          item.remove();
        }
      });
    });
    this.indicators.clear();
  }

  // Очистка конкретного индикатора
  clearIndicator(indicatorName: string) {
    const indicatorItems = this.indicators.get(indicatorName);
    if (indicatorItems) {
      indicatorItems.forEach((item, index) => {
        if (item) {
          try {
            // Детальная диагностика типа элемента
            const itemType = item.constructor?.name || 'Unknown';
            const hasRemove = typeof item.remove === 'function';

            console.log(`Удаляем индикатор ${index} в ${indicatorName}: тип=${itemType}, hasRemove=${hasRemove}`);

            // Для серий с методом remove() используем item.remove()
            if (hasRemove) {
              item.remove();
              console.log(`✅ Индикатор ${index} в ${indicatorName} успешно удален через remove()`);
            }
            // Для SeriesApi без метода remove() используем chart.removeSeries()
            // Это основной случай для LineSeries, CandlestickSeries, HistogramSeries
            else if (itemType === 'SeriesApi' || itemType.includes('Series')) {
              this.chart.removeSeries(item);
              console.log(`✅ SeriesApi ${index} в ${indicatorName} успешно удален через chart.removeSeries()`);
            }
            // Для всех остальных случаев пытаемся удалить через chart.removeSeries()
            else {
              this.chart.removeSeries(item);
              console.log(`✅ Элемент ${index} в ${indicatorName} (тип: ${itemType}) удален через chart.removeSeries()`);
            }
          } catch (error) {
            console.error(`❌ Ошибка при удалении индикатора ${index} в ${indicatorName}:`, error);
            // Попробуем альтернативный способ удаления
            try {
              if (typeof item.remove === 'function') {
                item.remove();
                console.log(`✅ Индикатор ${index} в ${indicatorName} удален альтернативным способом через remove()`);
              }
            } catch (secondError) {
              console.error(`❌ Альтернативный способ удаления также не сработал:`, secondError);
            }
          }
        }
      });

      // Специальная обработка для индикаторов с маркерами
      if (indicatorName === 'parabolicSAR') {
        // Очищаем маркеры с основной серии свечей
        this.candlestickSeries.setMarkers([]);
        console.log(`✅ Маркеры для индикатора ${indicatorName} очищены`);
      }

      this.indicators.delete(indicatorName);
      console.log(`✅ Индикатор ${indicatorName} полностью очищен`);
    } else {
      console.log(`ℹ️ Индикатор ${indicatorName} не найден или уже пуст`);
    }
  }

  // Добавление скользящих средних
  addMovingAverages(candleData: any[]) {
    this.clearIndicator('movingAverages');
    const indicatorItems: any[] = [];

    // MA_20 - зеленая линия
    const ma20Series = this.chart.addLineSeries({
      color: '#26A69A',
      lineWidth: 2,
      lineStyle: LineStyle.Solid,
      title: 'MA 20',
    });

    // MA_50 - синяя линия
    const ma50Series = this.chart.addLineSeries({
      color: '#2196F3',
      lineWidth: 2,
      lineStyle: LineStyle.Solid,
      title: 'MA 50',
    });

    // MA_100 - оранжевая линия
    const ma100Series = this.chart.addLineSeries({
      color: '#FF9800',
      lineWidth: 2,
      lineStyle: LineStyle.Solid,
      title: 'MA 100',
    });

    // MA_200 - красная линия
    const ma200Series = this.chart.addLineSeries({
      color: '#F44336',
      lineWidth: 2,
      lineStyle: LineStyle.Solid,
      title: 'MA 200',
    });

    // Подготавливаем данные для каждой MA
    const ma20Data = candleData.filter(candle => candle.MA_20).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.MA_20,
    }));

    const ma50Data = candleData.filter(candle => candle.MA_50).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.MA_50,
    }));

    const ma100Data = candleData.filter(candle => candle.MA_100).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.MA_100,
    }));

    const ma200Data = candleData.filter(candle => candle.MA_200).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.MA_200,
    }));

    // Устанавливаем данные
    ma20Series.setData(ma20Data);
    ma50Series.setData(ma50Data);
    ma100Series.setData(ma100Data);
    ma200Series.setData(ma200Data);

    indicatorItems.push(ma20Series, ma50Series, ma100Series, ma200Series);
    this.indicators.set('movingAverages', indicatorItems);
  }

  // Добавление полос Боллинджера
  addBollingerBands(candleData: any[]) {
    this.clearIndicator('bollingerBands');
    const indicatorItems: any[] = [];

    // Верхняя полоса
    const upperBandSeries = this.chart.addLineSeries({
      color: '#9C27B0',
      lineWidth: 1,
      lineStyle: LineStyle.Dashed,
      title: 'Bollinger Upper',
    });

    // Средняя линия
    const middleBandSeries = this.chart.addLineSeries({
      color: '#9C27B0',
      lineWidth: 2,
      lineStyle: LineStyle.Solid,
      title: 'Bollinger Middle',
    });

    // Нижняя полоса
    const lowerBandSeries = this.chart.addLineSeries({
      color: '#9C27B0',
      lineWidth: 1,
      lineStyle: LineStyle.Dashed,
      title: 'Bollinger Lower',
    });

    // Подготавливаем данные
    const upperData = candleData.filter(candle => candle.Bollinger_Upper).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.Bollinger_Upper,
    }));

    const middleData = candleData.filter(candle => candle.Bollinger_Middle).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.Bollinger_Middle,
    }));

    const lowerData = candleData.filter(candle => candle.Bollinger_Lower).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.Bollinger_Lower,
    }));

    // Устанавливаем данные
    upperBandSeries.setData(upperData);
    middleBandSeries.setData(middleData);
    lowerBandSeries.setData(lowerData);

    indicatorItems.push(upperBandSeries, middleBandSeries, lowerBandSeries);
    this.indicators.set('bollingerBands', indicatorItems);
  }

  // Добавление облака Ишимоку
  addIchimokuCloud(candleData: any[]) {
    this.clearIndicator('ichimokuCloud');
    const indicatorItems: any[] = [];

    // Tenkan-sen (Conversion Line)
    const conversionLineSeries = this.chart.addLineSeries({
      color: '#FF5722',
      lineWidth: 1,
      lineStyle: LineStyle.Solid,
      title: 'Tenkan-sen',
    });

    // Kijun-sen (Base Line)
    const baseLineSeries = this.chart.addLineSeries({
      color: '#3F51B5',
      lineWidth: 1,
      lineStyle: LineStyle.Solid,
      title: 'Kijun-sen',
    });

    // Senkou Span A
    const spanASeries = this.chart.addLineSeries({
      color: 'rgba(76, 175, 80, 0.3)',
      lineWidth: 1,
      lineStyle: LineStyle.Solid,
      title: 'Senkou Span A',
    });

    // Senkou Span B
    const spanBSeries = this.chart.addLineSeries({
      color: 'rgba(244, 67, 54, 0.3)',
      lineWidth: 1,
      lineStyle: LineStyle.Solid,
      title: 'Senkou Span B',
    });

    // Подготавливаем данные
    const conversionData = candleData.filter(candle => candle.Ichimoku_Conversion_Line).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.Ichimoku_Conversion_Line,
    }));

    const baseData = candleData.filter(candle => candle.Ichimoku_Base_Line).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.Ichimoku_Base_Line,
    }));

    const spanAData = candleData.filter(candle => candle.Ichimoku_A).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.Ichimoku_A,
    }));

    const spanBData = candleData.filter(candle => candle.Ichimoku_B).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.Ichimoku_B,
    }));

    // Устанавливаем данные
    conversionLineSeries.setData(conversionData);
    baseLineSeries.setData(baseData);
    spanASeries.setData(spanAData);
    spanBSeries.setData(spanBData);

    indicatorItems.push(conversionLineSeries, baseLineSeries, spanASeries, spanBSeries);
    this.indicators.set('ichimokuCloud', indicatorItems);
  }

  // Добавление Parabolic SAR
  addParabolicSAR(candleData: any[]) {
    this.clearIndicator('parabolicSAR');
    const indicatorItems: any[] = [];

    const sarSeries = this.chart.addLineSeries({
      color: '#FF9800',
      lineWidth: 1,
      title: 'Parabolic SAR',
    });

    // Создаем маркеры для SAR
    const sarMarkers = candleData
      .filter(candle => candle.Parabolic_SAR)
      .map(candle => ({
        time: toTimestamp(candle['Open Time']) as any,
        position: candle.Parabolic_SAR > candle.Close ? 'aboveBar' as const : 'belowBar' as const,
        color: '#FF9800',
        shape: 'circle' as const,
        size: 0.5,
      }));

    this.candlestickSeries.setMarkers(sarMarkers);
    indicatorItems.push(sarSeries);
    this.indicators.set('parabolicSAR', indicatorItems);
  }

  // Добавление VWAP
  addVWAP(candleData: any[]) {
    this.clearIndicator('vwap');
    const indicatorItems: any[] = [];

    const vwapSeries = this.chart.addLineSeries({
      color: '#607D8B',
      lineWidth: 2,
      lineStyle: LineStyle.Solid,
      title: 'VWAP',
    });

    const vwapData = candleData.filter(candle => candle.VWAP).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.VWAP,
    }));

    vwapSeries.setData(vwapData);
    indicatorItems.push(vwapSeries);
    this.indicators.set('vwap', indicatorItems);
  }

  // Добавление конвертов MA
  addMovingAverageEnvelopes(candleData: any[]) {
    this.clearIndicator('maEnvelopes');
    const indicatorItems: any[] = [];

    // Верхний конверт
    const upperEnvelopeSeries = this.chart.addLineSeries({
      color: '#4CAF50',
      lineWidth: 1,
      lineStyle: LineStyle.Dotted,
      title: 'MA Envelope Upper',
    });

    // Нижний конверт
    const lowerEnvelopeSeries = this.chart.addLineSeries({
      color: '#4CAF50',
      lineWidth: 1,
      lineStyle: LineStyle.Dotted,
      title: 'MA Envelope Lower',
    });

    // Подготавливаем данные
    const upperData = candleData.filter(candle => candle.Moving_Average_Envelope_Upper).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.Moving_Average_Envelope_Upper,
    }));

    const lowerData = candleData.filter(candle => candle.Moving_Average_Envelope_Lower).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.Moving_Average_Envelope_Lower,
    }));

    // Устанавливаем данные
    upperEnvelopeSeries.setData(upperData);
    lowerEnvelopeSeries.setData(lowerData);

    indicatorItems.push(upperEnvelopeSeries, lowerEnvelopeSeries);
    this.indicators.set('maEnvelopes', indicatorItems);
  }

  // Получение активных индикаторов
  getActiveIndicators(): string[] {
    return Array.from(this.indicators.keys());
  }
}
