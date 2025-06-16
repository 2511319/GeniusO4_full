import { useEffect, useRef } from 'react'
import { createChart } from 'lightweight-charts'

type Candle = {
  time: number
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

  useEffect(() => {
    if (!containerRef.current) return
    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: containerRef.current.clientHeight,
    })
    // cast chart to any to access addCandlestickSeries API
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const series = (chart as any).addCandlestickSeries()
    series.setData(data)
    chart.timeScale().fitContent()
    return () => {
      chart.remove()
    }
  }, [data])

  return <div ref={containerRef} className="w-full h-80" />
}
