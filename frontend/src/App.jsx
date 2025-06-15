import React, { useContext, useState } from 'react';
import { CssBaseline, AppBar, Toolbar, Typography, IconButton } from '@mui/material';
import LightModeIcon from '@mui/icons-material/LightMode';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import { ColorModeContext } from './components/ColorModeContext';
import Home from './pages/Home';
import About from './pages/About';

function InnerApp() {
  const { mode, toggle } = useContext(ColorModeContext);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [commentsOpen, setCommentsOpen] = useState(true);

  return (
    <>
      <CssBaseline />
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
          <Route path="/" element={
            <Home
              sidebarOpen={sidebarOpen}
              commentsOpen={commentsOpen}
              setSidebarOpen={setSidebarOpen}
              setCommentsOpen={setCommentsOpen}
            />
          } />
          <Route path="/about" element={<About />} />
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default function App() {
  return <InnerApp />;
}
