import { useState } from 'react';

interface NewAnalysisModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (ticker: string, timeframe: string, candleCount: number) => void;
}

const NewAnalysisModal: React.FC<NewAnalysisModalProps> = ({ isOpen, onClose, onSubmit }) => {
  const [ticker, setTicker] = useState('BTCUSDT');
  const [timeframe, setTimeframe] = useState('1h');
  const [candleCount, setCandleCount] = useState(100);

  const timeframes = [
    { value: '1m', label: '1 минута' },
    { value: '5m', label: '5 минут' },
    { value: '15m', label: '15 минут' },
    { value: '30m', label: '30 минут' },
    { value: '1h', label: '1 час' },
    { value: '4h', label: '4 часа' },
    { value: '1d', label: '1 день' },
    { value: '1w', label: '1 неделя' },
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (ticker.trim() && candleCount > 0) {
      onSubmit(ticker.trim().toUpperCase(), timeframe, candleCount);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-[#1e1e1e] rounded-lg p-6 w-full max-w-md mx-4 border border-gray-700">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-white">Новый анализ</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <span className="text-2xl">&times;</span>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="ticker" className="block text-sm font-medium text-gray-300 mb-2">
              Тикер
            </label>
            <input
              type="text"
              id="ticker"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Например: BTCUSDT"
              required
            />
          </div>

          <div>
            <label htmlFor="timeframe" className="block text-sm font-medium text-gray-300 mb-2">
              Таймфрейм
            </label>
            <select
              id="timeframe"
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {timeframes.map((tf) => (
                <option key={tf.value} value={tf.value}>
                  {tf.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="candleCount" className="block text-sm font-medium text-gray-300 mb-2">
              Количество свечей
            </label>
            <input
              type="number"
              id="candleCount"
              value={candleCount}
              onChange={(e) => setCandleCount(parseInt(e.target.value) || 0)}
              min="10"
              max="1000"
              className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md transition-colors"
            >
              Отмена
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
            >
              Запустить анализ
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NewAnalysisModal;
