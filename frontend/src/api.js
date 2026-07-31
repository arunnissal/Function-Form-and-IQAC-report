import axios from 'axios';

let rawURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1/';

// Ensure trailing slash
if (rawURL && !rawURL.endsWith('/')) {
  rawURL += '/';
}

// Auto-upgrade to HTTPS for production remote hosts if page is HTTPS
if (window.location.protocol === 'https:' && rawURL.startsWith('http://') && !rawURL.includes('localhost') && !rawURL.includes('127.0.0.1')) {
  rawURL = rawURL.replace('http://', 'https://');
}

export const baseURL = rawURL;

const api = axios.create({
  baseURL: baseURL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export default api;
