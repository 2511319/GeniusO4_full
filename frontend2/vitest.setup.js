import '@testing-library/jest-dom';\nObject.defineProperty(window, 'matchMedia', { writable: true, value: () => ({ matches: false, addListener: () => {}, removeListener: () => {} }) });
