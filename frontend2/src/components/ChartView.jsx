import { useEffect, useRef } from 'react'
import { createChart } from 'lightweight-charts'

export default function ChartView({ data, overlays = {}, visible = {} }) {
  const containerRef = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!containerRef.current) return
    if (!chartRef.current) {
      chartRef.current = createChart(containerRef.current, {
        height: 400,
        layout: { background: { type: 'solid', color: 'transparent' } },
      })
    }
    const chart = chartRef.current
    chart.remove(); // Ensure no duplicates
    chartRef.current = createChart(containerRef.current, {
      height: 400,
      layout: { background: { type: 'solid', color: 'transparent' } },
    })
    const candlestick = chartRef.current.addCandlestickSeries()
    candlestick.setData(data)
    if (visible.support_resistance_levels && overlays.support_resistance_levels) {
      overlays.support_resistance_levels.forEach((level) => {
        chartRef.current.addLineSeries({ color: 'blue' }).setData(level)
      })
    }
    if (visible.trend_lines && overlays.trend_lines) {
      overlays.trend_lines.forEach((line) => {
        chartRef.current.addLineSeries({ color: 'green' }).setData(line)
      })
    }
    if (visible.fibonacci_analysis && overlays.fibonacci_analysis) {
      overlays.fibonacci_analysis.forEach((line) => {
        chartRef.current.addLineSeries({ color: 'orange' }).setData(line)
      })
    }
  }, [data, overlays, visible])

  return <div ref={containerRef} className="w-full" />
}
