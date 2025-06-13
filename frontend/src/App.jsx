import React, { useContext } from 'react';
import { CssBaseline, AppBar, Toolbar, Typography, IconButton, Box } from '@mui/material';
import LightModeIcon from '@mui/icons-material/LightMode';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import ColorModeProvider, { ColorModeContext } from './ColorModeContext';
import Home from './pages/Home';
import About from './pages/About';

function InnerApp() {
  const { mode, toggle } = useContext(ColorModeContext);

  return (
    <>
      <CssBaseline />
      <Box display="flex" gap={2} height="100vh" p={1}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              ChartGenius
            </Typography>
            <IconButton color="inherit" onClick={toggle}>
              {mode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>
          </Toolbar>
        </AppBar>

        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </BrowserRouter>
      </Box>
    </>
  );
}

export default function App() {
  return (
    <ColorModeProvider>
      <InnerApp />
    </ColorModeProvider>
  );
}
