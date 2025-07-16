import { useEffect, useState } from 'react';
import Chart from './components/Chart';
import AnalysisPanel from './components/AnalysisPanel';
import Controls from './components/Controls';
import NewAnalysisModal from './components/NewAnalysisModal';
import UserProfileMenu from './components/UserProfileMenu';
import ElementDetailsPanel from './components/ElementDetailsPanel';
import { candleData, aiResponseData } from './api/dataLoader';

type TogglesState = {
  [key: string]: boolean;
};

function App() {
  const [toggles, setToggles] = useState<TogglesState>({});
  const [isNewAnalysisModalOpen, setIsNewAnalysisModalOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  const handleToggle = (itemName: string) => {
    setToggles(prev => ({
      ...prev,
      [itemName]: !prev[itemName],
    }));
  };

  const handleNewAnalysis = (ticker: string, timeframe: string, candleCount: number) => {
    console.log('Новый анализ:', { ticker, timeframe, candleCount });
    // Здесь будет логика запроса к API
    setIsNewAnalysisModalOpen(false);
  };

  useEffect(() => {
    // @ts-ignore
    // lucide.createIcons();
  }, []);

  return (
    <div className="h-screen flex flex-col bg-[#121212] text-white">
      <header className="flex justify-between items-center p-4 border-b border-gray-800">
        <div className="flex items-center gap-4">
          <img src="https://i.imgur.com/yVbACrx.png" alt="Crypto AI Analyst Logo" className="h-10 w-10" />
          <h1 className="text-2xl font-bold">Crypto AI Analyst</h1>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => setIsNewAnalysisModalOpen(true)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
          >
            <span className="text-lg">+</span>
            Новый анализ
          </button>
          <div className="relative">
            <button
              onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
              className="flex items-center gap-2 bg-gray-700/50 hover:bg-gray-700 p-2 rounded-lg transition-colors"
            >
              <img src="https://i.pravatar.cc/40" alt="User Avatar" className="h-8 w-8 rounded-full" />
              <span className="text-sm">Пользователь</span>
            </button>
            <UserProfileMenu
              isOpen={isUserMenuOpen}
              onClose={() => setIsUserMenuOpen(false)}
            />
          </div>
        </div>
      </header>

      <Controls toggles={toggles} onToggle={handleToggle} />

      <main className="flex-grow flex" style={{ minHeight: 0 }}>
        <Chart
          candleData={candleData}
          analysisData={aiResponseData}
          toggles={toggles}
        />
        <div className="flex">
          <AnalysisPanel
            analysisData={aiResponseData}
            toggles={toggles}
          />
          <ElementDetailsPanel
            analysisData={aiResponseData}
            toggles={toggles}
          />
        </div>
      </main>

      <NewAnalysisModal
        isOpen={isNewAnalysisModalOpen}
        onClose={() => setIsNewAnalysisModalOpen(false)}
        onSubmit={handleNewAnalysis}
      />
    </div>
  );
}

export default App;
