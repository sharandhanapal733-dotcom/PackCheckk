import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
});

// Request Interceptor: Attach JWT token if present
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('packcheck_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401 unauth
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Don't auto-redirect if checking /api/auth/login or /api/auth/me
      if (!error.config.url.includes('/auth/login')) {
        localStorage.removeItem('packcheck_token');
        localStorage.removeItem('packcheck_user');
        if (window.location.pathname !== '/login' && window.location.pathname !== '/') {
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (data) => api.post('/auth/register', data),
  getMe: () => api.get('/auth/me'),
};

export const inspectionsAPI = {
  create: (data) => api.post('/inspections', data),
  list: (params) => api.get('/inspections', { params }),
  get: (id) => api.get(`/inspections/${id}`),
  uploadImages: (id, formData) =>
    api.post(`/inspections/${id}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  process: (id) => api.post(`/inspections/${id}/process`),
  correctField: (id, fieldId, data) => api.patch(`/inspections/${id}/fields/${fieldId}`, data),
  getOCR: (id) => api.get(`/inspections/${id}/ocr`),
  getCompliance: (id) => api.get(`/inspections/${id}/compliance`),
};

export const dashboardAPI = {
  get: () => api.get('/dashboard'),
};

export const reportsAPI = {
  generate: (inspectionId) => api.post(`/reports/${inspectionId}/generate`),
  downloadPdf: async (reportId, filename = 'inspection_report.pdf') => {
    const response = await api.get(`/reports/${reportId}/download`, {
      responseType: 'blob',
    });
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    setTimeout(() => {
      window.URL.revokeObjectURL(url);
      link.remove();
    }, 100);
    return true;
  },
  downloadInspectionPdf: async (inspectionId, filename = `inspection_${inspectionId}.pdf`) => {
    const response = await api.get(`/reports/inspection/${inspectionId}/pdf`, {
      responseType: 'blob',
    });
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    setTimeout(() => {
      window.URL.revokeObjectURL(url);
      link.remove();
    }, 100);
    return true;
  },
  getDownloadUrl: (reportId) => {
    const token = localStorage.getItem('packcheck_token');
    return `/api/reports/${reportId}/download${token ? `?token=${encodeURIComponent(token)}` : ''}`;
  },
  getInspectionPdfUrl: (inspectionId) => {
    const token = localStorage.getItem('packcheck_token');
    return `/api/reports/inspection/${inspectionId}/pdf${token ? `?token=${encodeURIComponent(token)}` : ''}`;
  },
};

export const productsAPI = {
  list: (params) => api.get('/products', { params }),
  getHistory: (id) => api.get(`/products/${id}/history`),
};

export const rulesAPI = {
  list: () => api.get('/rules'),
  create: (data) => api.post('/rules', data),
  update: (id, data) => api.put(`/rules/${id}`, data),
  delete: (id) => api.delete(`/rules/${id}`),
};

export default api;
