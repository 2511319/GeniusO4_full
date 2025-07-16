import { createChart, IChartApi, ISeriesApi, CandlestickData, ColorType } from 'lightweight-charts';
import { useEffect, useRef } from 'react';
import { ChartAnalysisLayers } from './ChartAnalysisLayers';
import { ChartIndicators } from './ChartIndicators';
import { ChartSubPanels } from './ChartSubPanels';

interface ChartProps {
  candleData: any[];
  analysisData: any;
  toggles: { [key: string]: boolean };
}

const Chart = ({ candleData, analysisData, toggles }: ChartProps) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const analysisLayersRef = useRef<ChartAnalysisLayers | null>(null);
  const indicatorsRef = useRef<ChartIndicators | null>(null);
  const subPanelsRef = useRef<ChartSubPanels | null>(null);

  // Эффект для создания графика (выполняется один раз)
  useEffect(() => {
    if (!chartContainerRef.current || chartRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      autoSize: true,
      layout: {
        background: { type: ColorType.Solid, color: '#121212' },
        textColor: '#FFFFFF',
      },
      grid: { vertLines: { color: '#2A2A2A' }, horzLines: { color: '#2A2A2A' } },
      timeScale: { borderColor: '#4A4A4A' },
    });

    chartRef.current = chart;
    seriesRef.current = chart.addCandlestickSeries({
      upColor: '#26A69A',
      downColor: '#EF5350',
      borderVisible: false,
      wickUpColor: '#26A69A',
      wickDownColor: '#EF5350',
    });

    // Инициализируем слои анализа и индикаторы
    analysisLayersRef.current = new ChartAnalysisLayers(chart, seriesRef.current);
    indicatorsRef.current = new ChartIndicators(chart, seriesRef.current);
    subPanelsRef.current = new ChartSubPanels(chart);

    return () => {
      if (subPanelsRef.current) {
        subPanelsRef.current.clearAllSubPanels();
        subPanelsRef.current = null;
      }
      if (indicatorsRef.current) {
        indicatorsRef.current.clearAllIndicators();
        indicatorsRef.current = null;
      }
      if (analysisLayersRef.current) {
        analysisLayersRef.current.clearAllLayers();
        analysisLayersRef.current = null;
      }
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, []);

  // Эффект для обновления данных свечей
  useEffect(() => {
    if (!seriesRef.current || !candleData || candleData.length === 0) return;

    const toTimestamp = (strDate: string) => new Date(strDate).getTime() / 1000;
    const formattedCandleData: CandlestickData[] = candleData.map(d => ({
      time: toTimestamp(d['Open Time']) as any,
      open: d.Open,
      high: d.High,
      low: d.Low,
      close: d.Close,
    }));

    seriesRef.current.setData(formattedCandleData);
    chartRef.current?.timeScale().fitContent();
  }, [candleData]);

  // Эффект для обновления аналитических слоев
  useEffect(() => {
    if (!chartRef.current || !seriesRef.current || !analysisData || !analysisLayersRef.current) return;

    const layers = analysisLayersRef.current;

    // Уровни поддержки/сопротивления
    if (toggles['Уровни поддержки/сопротивления']) {
      if (analysisData.support_resistance_levels) {
        const supports = analysisData.support_resistance_levels.supports || [];
        const resistances = analysisData.support_resistance_levels.resistances || [];
        layers.addSupportResistanceLevels(supports, resistances);
      }
    } else {
      layers.clearLayer('supportResistance');
    }

    // Линии тренда
    if (toggles['Линии тренда']) {
      if (analysisData.trend_lines?.lines) {
        layers.addTrendLines(analysisData.trend_lines.lines);
      }
    } else {
      layers.clearLayer('trendLines');
    }

    // Коррекция по Фибоначчи
    if (toggles['Коррекция по Фибоначчи']) {
      if (analysisData.fibonacci_analysis) {
        layers.addFibonacciLevels(analysisData.fibonacci_analysis);
      }
    } else {
      layers.clearLayer('fibonacci');
    }

    // Зоны дисбаланса
    if (toggles['Зоны дисбаланса']) {
      if (analysisData.imbalances) {
        layers.addImbalanceZones(analysisData.imbalances);
      }
    } else {
      layers.clearLayer('imbalances');
    }

    // Незавершенные зоны
    if (toggles['Незавершенные зоны']) {
      if (analysisData.unfinished_zones) {
        layers.addUnfinishedZones(analysisData.unfinished_zones);
      }
    } else {
      layers.clearLayer('unfinishedZones');
    }

    // Свечные паттерны
    if (toggles['Свечные паттерны']) {
      if (analysisData.candlestick_patterns) {
        layers.addCandlestickPatterns(analysisData.candlestick_patterns);
      }
    } else {
      layers.clearLayer('candlestickPatterns');
    }

    // Дивергенции
    if (toggles['Дивергенции']) {
      if (analysisData.divergence_analysis) {
        layers.addDivergences(analysisData.divergence_analysis);
      }
    } else {
      layers.clearLayer('divergences');
    }

    // Волны Эллиотта
    if (toggles['Волны Эллиотта']) {
      if (analysisData.elliott_wave_analysis) {
        layers.addElliottWaves(analysisData.elliott_wave_analysis);
      }
    } else {
      layers.clearLayer('elliottWaves');
    }

    // Визуальный прогноз
    if (toggles['Визуальный прогноз']) {
      if (analysisData.price_prediction) {
        layers.addPricePrediction(analysisData.price_prediction);
      }
    } else {
      layers.clearLayer('pricePrediction');
    }

    // Торговые рекомендации
    if (toggles['Показать сделки']) {
      if (analysisData.recommendations?.trading_strategies) {
        layers.addTradingRecommendations(analysisData.recommendations.trading_strategies);
      }
    } else {
      layers.clearLayer('tradingRecommendations');
    }

  }, [analysisData, toggles]);

  // Эффект для обновления технических индикаторов
  useEffect(() => {
    if (!chartRef.current || !seriesRef.current || !candleData || !indicatorsRef.current || !subPanelsRef.current) return;

    const indicators = indicatorsRef.current;
    const subPanels = subPanelsRef.current;

    // Индикаторы на основной панели
    if (toggles['Скользящие средние']) {
      indicators.addMovingAverages(candleData);
    } else {
      indicators.clearIndicator('movingAverages');
    }

    if (toggles['Полосы Боллинджера']) {
      indicators.addBollingerBands(candleData);
    } else {
      indicators.clearIndicator('bollingerBands');
    }

    if (toggles['Облако Ишимоку']) {
      indicators.addIchimokuCloud(candleData);
    } else {
      indicators.clearIndicator('ichimokuCloud');
    }

    if (toggles['Parabolic SAR']) {
      indicators.addParabolicSAR(candleData);
    } else {
      indicators.clearIndicator('parabolicSAR');
    }

    if (toggles['VWAP']) {
      indicators.addVWAP(candleData);
    } else {
      indicators.clearIndicator('vwap');
    }

    if (toggles['Конверты MA']) {
      indicators.addMovingAverageEnvelopes(candleData);
    } else {
      indicators.clearIndicator('maEnvelopes');
    }

    // Индикаторы на отдельных панелях
    if (toggles['Объем']) {
      subPanels.addVolumePanel(candleData);
    } else {
      subPanels.clearSubPanel('volume');
    }

    if (toggles['RSI']) {
      subPanels.addRSIPanel(candleData);
    } else {
      subPanels.clearSubPanel('rsi');
    }

    if (toggles['MACD']) {
      subPanels.addMACDPanel(candleData);
    } else {
      subPanels.clearSubPanel('macd');
    }

    if (toggles['Stochastic']) {
      subPanels.addStochasticPanel(candleData);
    } else {
      subPanels.clearSubPanel('stochastic');
    }

    if (toggles['Williams %R']) {
      subPanels.addWilliamsRPanel(candleData);
    } else {
      subPanels.clearSubPanel('williamsR');
    }

    if (toggles['ADX']) {
      subPanels.addADXPanel(candleData);
    } else {
      subPanels.clearSubPanel('adx');
    }

    if (toggles['ATR']) {
      subPanels.addATRPanel(candleData);
    } else {
      subPanels.clearSubPanel('atr');
    }

    if (toggles['OBV']) {
      subPanels.addOBVPanel(candleData);
    } else {
      subPanels.clearSubPanel('obv');
    }

  }, [candleData, toggles]);

  return <div ref={chartContainerRef} className="flex-grow relative" />;
};

export default Chart;
