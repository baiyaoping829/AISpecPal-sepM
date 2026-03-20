import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器，添加token
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器，处理错误
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      const authStore = useAuthStore()
      authStore.removeToken()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 认证相关API
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

// 规范标准相关API
export const specificationsAPI = {
  getList: () => api.get('/specifications/'),
  getDetail: (id) => api.get(`/specifications/${id}`),
  create: (data) => api.post('/specifications/', data),
  update: (id, data) => api.put(`/specifications/${id}`, data),
  delete: (id) => api.delete(`/specifications/${id}`)
}

// 版本相关API
export const versionsAPI = {
  getBySpecification: (specId) => api.get(`/versions/specification/${specId}`),
  getDetail: (id) => api.get(`/versions/${id}`),
  create: (data) => api.post('/versions/', data),
  update: (id, data) => api.put(`/versions/${id}`, data),
  delete: (id) => api.delete(`/versions/${id}`)
}

// 关联关系相关API
export const relationsAPI = {
  getBySource: (sourceId) => api.get(`/relations/source/${sourceId}`),
  getByTarget: (targetId) => api.get(`/relations/target/${targetId}`),
  getDetail: (id) => api.get(`/relations/${id}`),
  create: (data) => api.post('/relations/', data),
  update: (id, data) => api.put(`/relations/${id}`, data),
  delete: (id) => api.delete(`/relations/${id}`)
}

// 文件相关API
export const filesAPI = {
  upload: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  download: (filePath) => api.get(`/files/download?file_path=${filePath}`, {
    responseType: 'blob'
  })
}

export default api