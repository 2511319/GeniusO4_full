// BUILD_HASH_FORCE_CHANGE: 1.0.16-20250622-210500
import { configureStore, createSlice } from '@reduxjs/toolkit';
import { API_URL } from './config';

// Утилита для декодирования JWT токена
const decodeToken = (token) => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload;
  } catch {
    return null;
  }
};

// Утилита для проверки истечения токена (с запасом 5 минут)
const isTokenExpiringSoon = (token) => {
  const payload = decodeToken(token);
  if (!payload || !payload.exp) return true;

  const currentTime = Math.floor(Date.now() / 1000);
  const expirationTime = payload.exp;
  const fiveMinutes = 5 * 60;

  return (expirationTime - currentTime) < fiveMinutes;
};

const tokenSlice = createSlice({
  name: 'auth',
  initialState: {
    token: localStorage.getItem('jwt') || '',
    user: null,
    isInitialized: false,
    refreshing: false
  },
  reducers: {
    setToken(state, action) {
      state.token = action.payload;
      if (action.payload) {
        localStorage.setItem('jwt', action.payload);
        // В продакшн не логируем токены
        if (process.env.NODE_ENV !== 'production') {
          console.log('Токен сохранен:', action.payload.substring(0, 20) + '...');
        }
      } else {
        localStorage.removeItem('jwt');
        if (process.env.NODE_ENV !== 'production') {
          console.log('Токен удален');
        }
      }
    },
    setUser(state, action) {
      state.user = action.payload;
    },
    clearAuth(state) {
      state.token = '';
      state.user = null;
      state.isInitialized = true;
      localStorage.removeItem('jwt');
    },
    initializeAuth(state) {
      // Проверяем токен из localStorage
      const savedToken = localStorage.getItem('jwt');
      if (savedToken && savedToken !== state.token) {
        state.token = savedToken;
        if (process.env.NODE_ENV !== 'production') {
          console.log('Восстановлен токен из localStorage');
        }
      }
      state.isInitialized = true;
      if (process.env.NODE_ENV !== 'production') {
        console.log('Auth инициализирован, токен:', state.token ? 'есть' : 'отсутствует');
      }
    },
    setRefreshing(state, action) {
      state.refreshing = action.payload;
    },
    refreshTokenSuccess(state, action) {
      state.token = action.payload;
      state.refreshing = false;
      localStorage.setItem('jwt', action.payload);
      if (process.env.NODE_ENV !== 'production') {
        console.log('Токен успешно обновлен');
      }
    },
    refreshTokenFailure(state) {
      state.token = '';
      state.user = null;
      state.refreshing = false;
      state.isInitialized = true;
      localStorage.removeItem('jwt');
      if (process.env.NODE_ENV !== 'production') {
        console.log('Ошибка обновления токена, пользователь разлогинен');
      }
    }
  }
});

export const {
  setToken,
  setUser,
  clearAuth,
  initializeAuth,
  setRefreshing,
  refreshTokenSuccess,
  refreshTokenFailure
} = tokenSlice.actions;

// Async action для обновления токена
export const refreshToken = () => async (dispatch, getState) => {
  const { auth } = getState();

  if (auth.refreshing || !auth.token) {
    return;
  }

  dispatch(setRefreshing(true));

  try {
    const response = await fetch(`${API_URL}/api/auth/refresh-token`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${auth.token}`,
        'Content-Type': 'application/json'
      }
    });

    if (response.ok) {
      const data = await response.json();
      dispatch(refreshTokenSuccess(data.access_token));
    } else {
      throw new Error('Refresh failed');
    }
  } catch (error) {
    if (process.env.NODE_ENV !== 'production') {
      console.error('Ошибка обновления токена:', error);
    }
    dispatch(refreshTokenFailure());
  }
};

// Middleware для автоматического обновления токенов
const tokenRefreshMiddleware = (store) => (next) => (action) => {
  const result = next(action);

  // Проверяем токен после каждого действия
  const state = store.getState();
  const { token, refreshing } = state.auth;

  if (token && !refreshing && isTokenExpiringSoon(token)) {
    if (process.env.NODE_ENV !== 'production') {
      console.log('Токен скоро истечет, запускаем обновление...');
    }
    store.dispatch(refreshToken());
  }

  return result;
};

export const store = configureStore({
  reducer: { auth: tokenSlice.reducer },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      thunk: true
    }).concat(tokenRefreshMiddleware)
});
