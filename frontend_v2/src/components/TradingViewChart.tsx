import { useEffect, useRef } from 'react'
import { createChart, CandlestickSeries, type IChartApi, type UTCTimestamp } from 'lightweight-charts'

type Candle = {
  time: UTCTimestamp
  open: number
  high: number
  low: number
  close: number
}

interface Props {
  data: Candle[]
}

export default function TradingViewChart({ data }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ReturnType<IChartApi['addSeries']> | null>(null)

  useEffect(() => {
    if (!containerRef.current || chartRef.current) return
    chartRef.current = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: containerRef.current.clientHeight,
    })
    seriesRef.current = chartRef.current.addSeries(CandlestickSeries)
    return () => {
      chartRef.current?.remove()
      chartRef.current = null
      seriesRef.current = null
    }
  }, [])

  useEffect(() => {
    if (!seriesRef.current) return
    seriesRef.current.setData(data)
    chartRef.current?.timeScale().fitContent()
  }, [data])

  return <div ref={containerRef} className="w-full h-80" />
}
