import React, { createContext, useEffect, useMemo, useState } from 'react';

export const ColorModeContext = createContext({ mode: 'dark', toggle: () => {} });

export default function ColorModeProvider({ children }) {
  const [mode, setMode] = useState(() => localStorage.getItem('ui-theme') || 'dark');

  const colorMode = useMemo(
    () => ({
      mode,
      toggle: () =>
        setMode((prev) => {
          const next = prev === 'dark' ? 'light' : 'dark';
          localStorage.setItem('ui-theme', next);
          return next;
        }),
    }),
    [mode],
  );

  useEffect(() => {
    const root = document.documentElement;
    if (mode === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [mode]);

  return (
    <ColorModeContext.Provider value={colorMode}>
      {children}
    </ColorModeContext.Provider>
  );
}
