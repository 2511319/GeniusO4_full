import { render } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from './App'

vi.mock('./hooks/useAnalysis', () => ({
  default: () => ({ data: { ohlc: [], analysis: {} }, loading: false, error: null, refetch: () => {} })
}))

describe('App', () => {
  it('renders without crashing', () => {
    const { getByText } = render(<App />)
    expect(getByText('Обновить')).toBeTruthy()
  })
})
