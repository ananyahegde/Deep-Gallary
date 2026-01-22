import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: (username, password) =>
    api.post(
      '/token',
      new URLSearchParams({ username, password }),
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
    ),
  signup: (data) => api.post('/admins', data),
  getCurrentUser: () => api.get('/admins/me/'),
};

export const photographersAPI = {
  getAll: () => api.get('/admins'),
  getByUsername: (username) => api.get(`/admins?username=${username}`),
  update: (formData) => api.patch('/admins', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
};

export const projectsAPI = {
  getAll: () => api.get('/projects'),
  getByUsername: (username) => api.get(`/${username}/projects`),
  getById: (id) => api.get(`/projects/${id}`),
  create: (data) => api.post('/projects', data),
  update: (id, data) => api.patch(`/projects/${id}`, data),
  delete: (id) => api.delete(`/projects/${id}`),
};

export const imagesAPI = {
  getAll: () => api.get('/images'),
  getById: (id) => api.get(`/images/${id}`),
  getByProjectId: (projectId) => api.get(`/images?project_id=${projectId}`),
  getSimilar: (id, limit = 3) => api.get(`/images/${id}/similar?limit=${limit}`),
  search: (query) => api.get(`/images/search?q=${encodeURIComponent(query)}`),
  generatePreview: (formData) => api.post('/images/ai-preview', formData),
  upload: (projectId, formData) => api.post(`/images/${projectId}`, formData),
  update: (id, data) => api.patch(`/images/${id}`, data),
  delete: (id) => api.delete(`/images/${id}`),
};

export default api;
