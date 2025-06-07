import { createTheme } from '@mui/material';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#1976d2' },
    background: {
      default: '#121212',
      paper:   '#1d1d1d',
    },
  },
  typography: {
    fontFamily: "Roboto, 'Helvetica', 'Arial', sans-serif",
    h6: { fontWeight: 600 },
  },
});

export default theme;

