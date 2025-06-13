import React, { createContext, useMemo, useState } from 'react';
import { createTheme, ThemeProvider } from '@mui/material';

export const ColorModeContext = createContext({ toggle: () => {} });

export default function ColorModeProvider({ children }) {
  const [mode, setMode] = useState(() =>
    localStorage.getItem('ui-theme') || 'dark',
  );

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

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          primary: { main: '#1976d2' },
          background: {
            default: mode === 'dark' ? '#121212' : '#fafafa',
            paper: mode === 'dark' ? '#1d1d1d' : '#ffffff',
          },
        },
        typography: {
          fontFamily: "Roboto,'Helvetica','Arial',sans-serif",
          h6: { fontWeight: 600 },
        },
      }),
    [mode],
  );

  return (
    <ColorModeContext.Provider value={colorMode}>
      <ThemeProvider theme={theme}>{children}</ThemeProvider>
    </ColorModeContext.Provider>
  );
}
