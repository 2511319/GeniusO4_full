import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { Provider } from 'react-redux';
import { store } from './store';
import { MemoryRouter } from 'react-router-dom';
import App from './App';
import { describe, it, expect } from 'vitest';
describe('App', () => {
  it('renders navigation and home page', () => {
    render(
      <Provider store={store}>
        <MemoryRouter>
          <App />
        </MemoryRouter>
      </Provider>
    );
    expect(screen.getByText(/ChartGenius/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Запустить анализ/i })).toBeInTheDocument();
  });
});
