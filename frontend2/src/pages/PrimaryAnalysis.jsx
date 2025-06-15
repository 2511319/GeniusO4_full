export default function PrimaryAnalysis({ analysis }) {
  return (
    <div className="p-4 space-y-2">
      <h2 className="text-xl font-bold">Общий анализ</h2>
      <pre className="text-sm whitespace-pre-wrap">
        {JSON.stringify(analysis?.primary_analysis, null, 2)}
      </pre>
      <h3 className="text-lg font-semibold">Confidence</h3>
      <pre className="text-sm whitespace-pre-wrap">
        {JSON.stringify(analysis?.confidence_in_trading_decisions, null, 2)}
      </pre>
    </div>
  )
}
