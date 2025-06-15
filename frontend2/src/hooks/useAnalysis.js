import { useState, useEffect } from 'react'
import axios from 'axios'

export default function useAnalysis(params) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const resp = await axios.post('/api/analyze', params)
      setData(resp.data)
      localStorage.setItem('lastAnalysis', JSON.stringify(resp.data))
    } catch (e) {
      setError(e)
      const cached = localStorage.getItem('lastAnalysis')
      if (cached) setData(JSON.parse(cached))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return { data, loading, error, refetch: fetchData }
}
