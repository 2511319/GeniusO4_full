import { configureStore, createSlice } from '@reduxjs/toolkit';

const tokenSlice = createSlice({
  name: 'auth',
  initialState: { token: localStorage.getItem('jwt') || '' },
  reducers: {
    setToken(state, action) {
      state.token = action.payload;
      localStorage.setItem('jwt', action.payload);
    }
  }
});

export const { setToken } = tokenSlice.actions;

export const store = configureStore({
  reducer: { auth: tokenSlice.reducer }
});
