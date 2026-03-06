import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api';
const API_VERSION = import.meta.env.VITE_API_VERSION || 'v1';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/${API_VERSION}`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('astroai_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('astroai_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const exoplanetApi = {
  getAll: (params?: any) => api.get('/exoplanets', { params }),
  getById: (id: string) => api.get(`/exoplanets/${id}`),
  search: (query: string) => api.get('/exoplanets/search', { params: { q: query } }),
};

export const classificationApi = {
  classify: (formData: FormData) => 
    api.post('/classify', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  classifyBatch: (formData: FormData) => 
    api.post('/classify/batch', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getHistory: () => api.get('/classify/history'),
  deleteResult: (id: string) => api.delete(`/classify/history/${id}`),
};

export const authApi = {
  login: (email: string, password: string) => 
    api.post('/auth/login', { email, password }),
  register: (username: string, email: string, password: string) => 
    api.post('/auth/register', { username, email, password }),
  logout: () => api.post('/auth/logout'),
  me: () => api.get('/auth/me'),
};

export default api;
