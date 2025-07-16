// Класс для управления индикаторами на отдельных панелях (объем, осцилляторы)
import { IChartApi, LineStyle } from 'lightweight-charts';
import { toTimestamp } from '../utils/chartAnalysisUtils';

export class ChartSubPanels {
  private chart: IChartApi;
  private subPanels: Map<string, any[]> = new Map();

  constructor(chart: IChartApi) {
    this.chart = chart;
  }

  // Очистка всех подпанелей
  clearAllSubPanels() {
    this.subPanels.forEach((panelItems) => {
      panelItems.forEach((item) => {
        if (item && typeof item.remove === 'function') {
          item.remove();
        }
      });
    });
    this.subPanels.clear();
  }

  // Очистка конкретной подпанели
  clearSubPanel(panelName: string) {
    const panelItems = this.subPanels.get(panelName);
    if (panelItems) {
      panelItems.forEach((item, index) => {
        if (item) {
          try {
            // Детальная диагностика типа элемента
            const itemType = item.constructor?.name || 'Unknown';
            const hasRemove = typeof item.remove === 'function';

            console.log(`Удаляем подпанель ${index} в ${panelName}: тип=${itemType}, hasRemove=${hasRemove}`);

            // Для серий с методом remove() используем item.remove()
            if (hasRemove) {
              item.remove();
              console.log(`✅ Подпанель ${index} в ${panelName} успешно удалена через remove()`);
            }
            // Для SeriesApi без метода remove() используем chart.removeSeries()
            // Это основной случай для LineSeries, HistogramSeries
            else if (itemType === 'SeriesApi' || itemType.includes('Series')) {
              this.chart.removeSeries(item);
              console.log(`✅ SeriesApi ${index} в ${panelName} успешно удален через chart.removeSeries()`);
            }
            // Для всех остальных случаев пытаемся удалить через chart.removeSeries()
            else {
              this.chart.removeSeries(item);
              console.log(`✅ Элемент ${index} в ${panelName} (тип: ${itemType}) удален через chart.removeSeries()`);
            }
          } catch (error) {
            console.error(`❌ Ошибка при удалении подпанели ${index} в ${panelName}:`, error);
            // Попробуем альтернативный способ удаления
            try {
              if (typeof item.remove === 'function') {
                item.remove();
                console.log(`✅ Подпанель ${index} в ${panelName} удалена альтернативным способом через remove()`);
              }
            } catch (secondError) {
              console.error(`❌ Альтернативный способ удаления также не сработал:`, secondError);
            }
          }
        }
      });

      this.subPanels.delete(panelName);
      console.log(`✅ Подпанель ${panelName} полностью очищена`);
    } else {
      console.log(`ℹ️ Подпанель ${panelName} не найдена или уже пуста`);
    }
  }

  // Добавление панели объема
  addVolumePanel(candleData: any[]) {
    this.clearSubPanel('volume');
    const panelItems: any[] = [];

    const volumeSeries = this.chart.addHistogramSeries({
      color: '#26A69A',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: 'volume',
    });

    const volumeData = candleData.filter(candle => candle.Volume).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.Volume,
      color: candle.Close >= candle.Open ? '#26A69A' : '#EF5350',
    }));

    volumeSeries.setData(volumeData);
    panelItems.push(volumeSeries);
    this.subPanels.set('volume', panelItems);
  }

  // Добавление панели RSI
  addRSIPanel(candleData: any[]) {
    this.clearSubPanel('rsi');
    const panelItems: any[] = [];

    const rsiSeries = this.chart.addLineSeries({
      color: '#2196F3',
      lineWidth: 2,
      lineStyle: LineStyle.Solid,
      priceScaleId: 'rsi',
    });

    // Добавляем горизонтальные линии для уровней 30 и 70
    const rsiUpperLine = this.chart.addLineSeries({
      color: '#F44336',
      lineWidth: 1,
      lineStyle: LineStyle.Dashed,
      priceScaleId: 'rsi',
    });

    const rsiLowerLine = this.chart.addLineSeries({
      color: '#4CAF50',
      lineWidth: 1,
      lineStyle: LineStyle.Dashed,
      priceScaleId: 'rsi',
    });

    const rsiData = candleData.filter(candle => candle.RSI).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.RSI,
    }));

    // Данные для горизонтальных линий
    const upperLineData = rsiData.map(item => ({ time: item.time, value: 70 }));
    const lowerLineData = rsiData.map(item => ({ time: item.time, value: 30 }));

    rsiSeries.setData(rsiData);
    rsiUpperLine.setData(upperLineData);
    rsiLowerLine.setData(lowerLineData);

    panelItems.push(rsiSeries, rsiUpperLine, rsiLowerLine);
    this.subPanels.set('rsi', panelItems);
  }

  // Добавление панели MACD
  addMACDPanel(candleData: any[]) {
    this.clearSubPanel('macd');
    const panelItems: any[] = [];

    // MACD линия
    const macdSeries = this.chart.addLineSeries({
      color: '#2196F3',
      lineWidth: 2,
      lineStyle: LineStyle.Solid,
      priceScaleId: 'macd',
    });

    // Signal линия
    const signalSeries = this.chart.addLineSeries({
      color: '#FF9800',
      lineWidth: 2,
      lineStyle: LineStyle.Solid,
      priceScaleId: 'macd',
    });

    // Histogram
    const histogramSeries = this.chart.addHistogramSeries({
      color: '#9C27B0',
      priceScaleId: 'macd',
    });

    const macdData = candleData.filter(candle => candle.MACD).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.MACD,
    }));

    const signalData = candleData.filter(candle => candle.MACD_signal).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.MACD_signal,
    }));

    const histogramData = candleData.filter(candle => candle.MACD_hist).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.MACD_hist,
      color: candle.MACD_hist >= 0 ? '#26A69A' : '#EF5350',
    }));

    macdSeries.setData(macdData);
    signalSeries.setData(signalData);
    histogramSeries.setData(histogramData);

    panelItems.push(macdSeries, signalSeries, histogramSeries);
    this.subPanels.set('macd', panelItems);
  }

  // Добавление панели Stochastic
  addStochasticPanel(candleData: any[]) {
    this.clearSubPanel('stochastic');
    const panelItems: any[] = [];

    const stochasticSeries = this.chart.addLineSeries({
      color: '#9C27B0',
      lineWidth: 2,
      lineStyle: LineStyle.Solid,
      priceScaleId: 'stochastic',
    });

    // Добавляем горизонтальные линии для уровней 20 и 80
    const stochUpperLine = this.chart.addLineSeries({
      color: '#F44336',
      lineWidth: 1,
      lineStyle: LineStyle.Dashed,
      priceScaleId: 'stochastic',
    });

    const stochLowerLine = this.chart.addLineSeries({
      color: '#4CAF50',
      lineWidth: 1,
      lineStyle: LineStyle.Dashed,
      priceScaleId: 'stochastic',
    });

    const stochasticData = candleData.filter(candle => candle.Stochastic_Oscillator).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.Stochastic_Oscillator,
    }));

    // Данные для горизонтальных линий
    const upperLineData = stochasticData.map(item => ({ time: item.time, value: 80 }));
    const lowerLineData = stochasticData.map(item => ({ time: item.time, value: 20 }));

    stochasticSeries.setData(stochasticData);
    stochUpperLine.setData(upperLineData);
    stochLowerLine.setData(lowerLineData);

    panelItems.push(stochasticSeries, stochUpperLine, stochLowerLine);
    this.subPanels.set('stochastic', panelItems);
  }

  // Добавление панели Williams %R
  addWilliamsRPanel(candleData: any[]) {
    this.clearSubPanel('williamsR');
    const panelItems: any[] = [];

    const williamsRSeries = this.chart.addLineSeries({
      color: '#FF5722',
      lineWidth: 2,
      lineStyle: LineStyle.Solid,
      priceScaleId: 'williamsR',
    });

    const williamsRData = candleData.filter(candle => candle['Williams_%R']).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle['Williams_%R'],
    }));

    williamsRSeries.setData(williamsRData);
    panelItems.push(williamsRSeries);
    this.subPanels.set('williamsR', panelItems);
  }

  // Добавление панели ADX
  addADXPanel(candleData: any[]) {
    this.clearSubPanel('adx');
    const panelItems: any[] = [];

    const adxSeries = this.chart.addLineSeries({
      color: '#795548',
      lineWidth: 2,
      lineStyle: LineStyle.Solid,
      priceScaleId: 'adx',
    });

    const adxData = candleData.filter(candle => candle.ADX).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.ADX,
    }));

    adxSeries.setData(adxData);
    panelItems.push(adxSeries);
    this.subPanels.set('adx', panelItems);
  }

  // Добавление панели ATR
  addATRPanel(candleData: any[]) {
    this.clearSubPanel('atr');
    const panelItems: any[] = [];

    const atrSeries = this.chart.addLineSeries({
      color: '#607D8B',
      lineWidth: 2,
      lineStyle: LineStyle.Solid,
      priceScaleId: 'atr',
    });

    const atrData = candleData.filter(candle => candle.ATR).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.ATR,
    }));

    atrSeries.setData(atrData);
    panelItems.push(atrSeries);
    this.subPanels.set('atr', panelItems);
  }

  // Добавление панели OBV
  addOBVPanel(candleData: any[]) {
    this.clearSubPanel('obv');
    const panelItems: any[] = [];

    const obvSeries = this.chart.addLineSeries({
      color: '#E91E63',
      lineWidth: 2,
      lineStyle: LineStyle.Solid,
      priceScaleId: 'obv',
    });

    const obvData = candleData.filter(candle => candle.OBV).map(candle => ({
      time: toTimestamp(candle['Open Time']) as any,
      value: candle.OBV,
    }));

    obvSeries.setData(obvData);
    panelItems.push(obvSeries);
    this.subPanels.set('obv', panelItems);
  }

  // Получение активных подпанелей
  getActiveSubPanels(): string[] {
    return Array.from(this.subPanels.keys());
  }
}
