export default function StrategyAnalysis({ analysis }) {
  return (
    <div className="p-4 space-y-4">
      <div>
        <h2 className="text-xl font-bold">Прогноз цены</h2>
        <pre className="text-sm whitespace-pre-wrap">
          {JSON.stringify(analysis?.price_prediction, null, 2)}
        </pre>
      </div>
      <div>
        <h2 className="text-xl font-bold">Торговые стратегии</h2>
        <pre className="text-sm whitespace-pre-wrap">
          {JSON.stringify(analysis?.trading_strategies, null, 2)}
        </pre>
      </div>
    </div>
  )
}
