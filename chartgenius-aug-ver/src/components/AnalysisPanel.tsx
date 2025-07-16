interface AnalysisPanelProps {
  analysisData: any;
  toggles: { [key: string]: boolean };
}

const AnalysisPanel = ({ analysisData, toggles }: AnalysisPanelProps) => {
  // Защитная проверка: если данных нет, не рендерим компонент
  if (!analysisData) {
    return <aside className="w-[400px] p-4">Загрузка данных анализа...</aside>;
  }

  // Временно используем toggles, чтобы TypeScript не выдавал ошибку
  console.log('Current toggles:', toggles);

  return (
    <aside className="w-[400px] glassmorphism rounded-lg m-4 p-4 flex flex-col">
      <h2 className="text-xl font-bold mb-4">Аналитика</h2>
      <div id="analysis-content" className="flex-grow overflow-y-auto">
        <div className="space-y-4">
          {/* Добавляем проверки на каждом уровне вложенности */}
          {analysisData.primary_analysis && (
            <div>
              <h3 className="font-bold text-lg">Основной анализ</h3>
              <p className="text-sm text-gray-400">{analysisData.primary_analysis.global_trend}</p>
              <p className="text-sm text-gray-400 mt-2">{analysisData.primary_analysis.local_trend}</p>
            </div>
          )}
          {analysisData.recommendations && analysisData.recommendations.trading_strategies && (
            <div>
              <h3 className="font-bold text-lg">Торговые рекомендации</h3>
              {analysisData.recommendations.trading_strategies.map((s: any, index: number) => (
                <div key={index} className="bg-gray-800/50 p-3 rounded-lg mt-2">
                  <p className="font-semibold">{s.strategy}</p>
                  {s.entry_point && (
                    <div className="text-xs grid grid-cols-3 gap-2 mt-1">
                      <span>Вход: {s.entry_point.Price}</span>
                      <span>Стоп: {s.stop_loss}</span>
                      <span>Тейк: {s.take_profit}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </aside>
  );
};

export default AnalysisPanel;
