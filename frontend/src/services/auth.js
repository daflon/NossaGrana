import api from './api';

export const authService = {
  async login(email, password) {
    const response = await api.post('/auth/login/', {
      email,
      password,
    });
    
    const { access, refresh } = response.data;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    
    return response.data;
  },

  async register(userData) {
    const response = await api.post('/auth/register/', userData);
    return response.data;
  },

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  },

  async getProfile() {
    const response = await api.get('/auth/profile/');
    return response.data;
  },
};