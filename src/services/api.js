import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Unauthenticated, redirect if on private page
      const currentPath = window.location.pathname;
      if (['/dashboard', '/upload', '/history'].some(p => currentPath.startsWith(p))) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
