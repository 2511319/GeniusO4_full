import React, { useState } from 'react';
import TechnicalIndicators from '../TechnicalIndicators';
import AdvancedIndicators from '../AdvancedIndicators';
import ModelAnalysisIndicators from '../ModelAnalysisIndicators';

const ControlPanel = ({
  symbol,
  setSymbol,
  limit,
  setLimit,
  interval,
  setInterval,
  loading,
  loadData,
  loadTestData,
  layers,
  toggleLayer,
  available,
  setLoading,
  setAnalysis,
  setData,
  setAvailable,
  analysis // Добавляем analysis для умного управления пространством
}) => {
  const [activeTab, setActiveTab] = useState('params');
  const [isParametersCollapsed, setIsParametersCollapsed] = useState(false);

  // Автоматически сворачиваем параметры после успешного анализа
  React.useEffect(() => {
    if (analysis && Object.keys(analysis).length > 0) {
      setIsParametersCollapsed(true);
    }
  }, [analysis]);

  const handleTestAPI = async () => {
    try {
      setLoading(true);
      const body = { symbol, interval, limit, indicators: layers };
      const res = await fetch('/api/analyze-test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const json = await res.json();
      setAnalysis(json.analysis);
      setData(json.ohlc || []);
      setAvailable(json.indicators || []);
    } catch (error) {
      console.error('Ошибка тестового анализа:', error);
      alert('Ошибка: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="pro-panel">
      {/* Профессиональная навигация */}
      <nav className="pro-nav">
        <button
          onClick={() => setActiveTab('params')}
          className={`pro-nav-item ${activeTab === 'params' ? 'active' : ''}`}
        >
          Параметры
        </button>
        <button
          onClick={() => setActiveTab('indicators')}
          className={`pro-nav-item ${activeTab === 'indicators' ? 'active' : ''}`}
        >
          Индикаторы
        </button>
        <button
          onClick={() => setActiveTab('analysis')}
          className={`pro-nav-item ${activeTab === 'analysis' ? 'active' : ''}`}
        >
          Анализ
        </button>
      </nav>

      {/* Содержимое вкладок */}
      <div className="p-4">
        {activeTab === 'params' && (
          <div className="pro-space-y-4">
            <div
              className="flex items-center justify-between cursor-pointer p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
              onClick={() => setIsParametersCollapsed(!isParametersCollapsed)}
            >
              <h3 className="text-lg font-semibold pro-text-primary">
                Параметры запроса
              </h3>
              <div className="flex items-center pro-space-x-2">
                {analysis && Object.keys(analysis).length > 0 && (
                  <span className="pro-status pro-status-success">
                    Анализ выполнен
                  </span>
                )}
                <span className={`transform transition-transform duration-200 ${isParametersCollapsed ? 'rotate-180' : ''}`}>
                  ▼
                </span>
              </div>
            </div>

            {/* Сворачиваемое содержимое параметров */}
            {!isParametersCollapsed && (
              <div className="pro-space-y-4 pt-2">
                <div>
                  <label className="block text-sm font-medium pro-text-secondary mb-1">
                    Тикер
                  </label>
                  <input
                    type="text"
                    value={symbol}
                    onChange={(e) => setSymbol(e.target.value)}
                    className="pro-input w-full"
                    placeholder="BTCUSDT"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium pro-text-secondary mb-1">
                    Количество свечей
                  </label>
                  <input
                    type="number"
                    value={limit}
                    onChange={(e) => setLimit(+e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Таймфрейм
                  </label>
                  <select
                    value={interval}
                    onChange={(e) => setInterval(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                  >
                    {['1m','5m','15m','1h','4h','1d'].map((tf) => (
                      <option key={tf} value={tf}>{tf}</option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2 pt-4">
                  <button
                    onClick={loadData}
                    disabled={loading}
                    className="w-full gradient-primary hover:shadow-glow-blue disabled:opacity-50 text-white font-medium py-2 px-4 rounded-md transition-all duration-300 btn-modern animate-pulse-glow"
                  >
                    {loading ? 'Анализ выполняется...' : 'Запустить анализ'}
                  </button>

                  <button
                    onClick={loadTestData}
                    className="w-full card-modern-dark hover:shadow-glow-purple text-white font-medium py-2 px-4 rounded-md transition-all duration-300 btn-modern"
                  >
                    Test (файл)
                  </button>

                  <button
                    onClick={handleTestAPI}
                    disabled={loading}
                    className="w-full card-modern-dark hover:shadow-glow-purple disabled:opacity-50 text-white font-medium py-2 px-4 rounded-md transition-all duration-300 btn-modern"
                  >
                    Test (API)
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'indicators' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                📊 Индикаторы графика
              </h3>
              <div className="grid grid-cols-1 gap-2">
                {['RSI','MACD','OBV','ATR','VWAP'].map((ind) => (
                  <label key={ind} className="flex items-center space-x-2 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded">
                    <input
                      type="checkbox"
                      checked={layers.includes(ind)}
                      onChange={() => toggleLayer(ind)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{ind}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                🔧 Технические индикаторы
              </h3>
              <TechnicalIndicators
                available={available}
                layers={layers}
                toggleLayer={toggleLayer}
              />
            </div>
          </div>
        )}

        {activeTab === 'analysis' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                🚀 Продвинутый анализ
              </h3>
              <AdvancedIndicators
                available={available}
                layers={layers}
                toggleLayer={toggleLayer}
              />
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                🤖 ИИ анализ
              </h3>
              <ModelAnalysisIndicators
                available={available}
                layers={layers}
                toggleLayer={toggleLayer}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ControlPanel;
