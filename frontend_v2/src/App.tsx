import TradingViewChart from './components/TradingViewChart'

const sampleData = [
  { time: 1640995200, open: 100, high: 105, low: 95, close: 102 },
  { time: 1641081600, open: 102, high: 110, low: 101, close: 108 },
  { time: 1641168000, open: 108, high: 112, low: 107, close: 111 },
]

export default function App() {
  return (
    <div className="p-4">
      <TradingViewChart data={sampleData} />
    </div>
  )
}
