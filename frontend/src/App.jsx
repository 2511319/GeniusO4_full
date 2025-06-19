import React, { useEffect } from 'react';
import { Routes, Route, Link, useSearchParams } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button } from '@mui/material';
import { useSelector, useDispatch } from 'react-redux';
import { setToken } from './store';
import Home from './pages/Home';
import About from './pages/About';
import Login from './pages/Login';
import UserDashboard from './pages/UserDashboard';

export default function App() {
  const token = useSelector((state) => state.auth.token);
  const dispatch = useDispatch();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    // Проверяем, есть ли токен в URL параметрах (от Telegram бота)
    const urlToken = searchParams.get('token');
    const page = searchParams.get('page');

    if (urlToken && !token) {
      dispatch(setToken(urlToken));
      // Не очищаем URL если это переход в личный кабинет
      if (page !== 'dashboard') {
        window.history.replaceState({}, document.title, window.location.pathname);
      }
    }
  }, [searchParams, token, dispatch]);

  const handleLogout = () => {
    dispatch(setToken(''));
    localStorage.removeItem('jwt');
  };

  // Проверяем, нужно ли показать личный кабинет
  const page = searchParams.get('page');
  if (page === 'dashboard') {
    return <UserDashboard />;
  }

  // Если пользователь не авторизован, показываем страницу логина
  if (!token) {
    return <Login />;
  }

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            GeniusO4
          </Typography>
          <Button color="inherit" component={Link} to="/">Home</Button>
          <Button color="inherit" component={Link} to="/about">About</Button>
          <Button color="inherit" component={Link} to="/?page=dashboard">Кабинет</Button>
          <Button color="inherit" onClick={handleLogout}>Выйти</Button>
        </Toolbar>
      </AppBar>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/dashboard" element={<UserDashboard />} />
      </Routes>
    </>
  );
}
