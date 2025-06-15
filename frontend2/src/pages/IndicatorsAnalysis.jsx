export default function IndicatorsAnalysis({ analysis }) {
  return (
    <div className="p-4">
      <h2 className="text-xl font-bold">Анализ индикаторов</h2>
      <pre className="text-sm whitespace-pre-wrap">
        {JSON.stringify(analysis?.indicators_analysis, null, 2)}
      </pre>
    </div>
  )
}
