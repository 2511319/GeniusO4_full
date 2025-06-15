import { useState } from 'react'
import { Tab } from '@headlessui/react'
import ChartView from './components/ChartView'
import useAnalysis from './hooks/useAnalysis'
import PrimaryAnalysis from './pages/PrimaryAnalysis'
import IndicatorsAnalysis from './pages/IndicatorsAnalysis'
import StrategyAnalysis from './pages/StrategyAnalysis'
import './index.css'

export default function App() {
  const { data, loading, error, refetch } = useAnalysis({ symbol: 'BTCUSDT', interval: '1d', limit: 100 })
  const [visible, setVisible] = useState({
    support_resistance_levels: true,
    trend_lines: true,
    fibonacci_analysis: true,
  })

  const toggle = (key) => setVisible((v) => ({ ...v, [key]: !v[key] }))

  if (loading) return <div className="p-4">Загрузка...</div>
  if (error) return <div className="p-4 text-red-500">Ошибка загрузки</div>

  return (
    <div className="container mx-auto p-4 space-y-4">
      <div className="flex space-x-4">
        {Object.keys(visible).map((key) => (
          <label key={key} className="flex items-center space-x-1">
            <input type="checkbox" checked={visible[key]} onChange={() => toggle(key)} />
            <span>{key}</span>
          </label>
        ))}
      </div>
      {data && (
        <ChartView data={data.ohlc} overlays={data.analysis} visible={visible} />
      )}
      <Tab.Group>
        <Tab.List className="flex space-x-1 rounded bg-gray-200 dark:bg-gray-800 p-1">
          <Tab className={({ selected }) => selected ? 'bg-white dark:bg-gray-700 px-3 py-1 rounded' : 'px-3 py-1'}>Анализ</Tab>
          <Tab className={({ selected }) => selected ? 'bg-white dark:bg-gray-700 px-3 py-1 rounded' : 'px-3 py-1'}>Индикаторы</Tab>
          <Tab className={({ selected }) => selected ? 'bg-white dark:bg-gray-700 px-3 py-1 rounded' : 'px-3 py-1'}>Стратегии</Tab>
        </Tab.List>
        <Tab.Panels className="mt-2">
          <Tab.Panel><PrimaryAnalysis analysis={data.analysis} /></Tab.Panel>
          <Tab.Panel><IndicatorsAnalysis analysis={data.analysis} /></Tab.Panel>
          <Tab.Panel><StrategyAnalysis analysis={data.analysis} /></Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
      <button onClick={refetch} className="mt-4 px-4 py-2 bg-blue-500 text-white rounded">Обновить</button>
    </div>
  )
}
