import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000,
});

export const generateQuestions = (data) => api.post('/api/generate', data);
export const getHistory = () => api.get('/api/history');
export const getSession = (id) => api.get(`/api/history/${id}`);
export const deleteSession = (id) => api.delete(`/api/history/${id}`);
export const exportSession = (id) => api.get(`/api/export/${id}`, { responseType: 'blob' });

export default api;
