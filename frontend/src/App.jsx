import React from 'react';
import { createChart } from 'lightweight-charts';
import { useEffect, useRef } from 'react';

export default function App() {
  const chartRef = useRef(null);

  useEffect(() => {
    const chart = createChart(chartRef.current, { height: 400 });
    const lineSeries = chart.addLineSeries();
    // пример данных
    lineSeries.setData([
      { time: '2024-05-21', value: 42000 },
      { time: '2024-05-22', value: 43000 },
      { time: '2024-05-23', value: 42500 },
    ]);
    return () => chart.remove();
  }, []);

  return <div ref={chartRef} />;
}
