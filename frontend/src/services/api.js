import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const uploadJSON = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await api.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  
  return response.data
}

export const estimateTranslation = async (jsonData, config) => {
  const response = await api.post('/api/translate/estimate', {
    target_language: config.targetLanguage,
    method: config.method,
    model: config.model,
    batch_size: config.batchSize,
    parallel: config.parallel,
    json_data: jsonData,
  })
  
  return response.data
}

export const startTranslation = async (jsonData, config) => {
  const response = await api.post('/api/translate/start', {
    target_language: config.targetLanguage,
    model: config.model,
    batch_size: config.batchSize,
    parallel: config.parallel,
    method: config.method,
    json_data: jsonData,
  })
  
  return response.data
}

export const getJobStatus = async (jobId) => {
  const response = await api.get(`/api/translate/${jobId}/status`)
  return response.data
}

export const getJobResult = async (jobId) => {
  const response = await api.get(`/api/translate/${jobId}/result`)
  return response.data
}

export const saveJobResult = async (jobId, filename = null) => {
  const response = await api.post(`/api/translate/${jobId}/save`, null, {
    params: filename ? { filename } : {},
  })
  return response.data
}

export const getModels = async () => {
  const response = await api.get('/api/models')
  return response.data
}

export const getLanguages = async () => {
  const response = await api.get('/api/languages')
  return response.data
}

export const listTranslatedFiles = async () => {
  const response = await api.get('/api/files')
  return response.data
}

export const getTranslatedFile = async (filename) => {
  const response = await api.get(`/api/files/${filename}`)
  return response.data
}

export const downloadTranslatedFile = async (filename) => {
  const response = await api.get(`/api/files/${filename}/download`, {
    responseType: 'blob',
  })
  
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

export const deleteTranslatedFile = async (filename) => {
  const response = await api.delete(`/api/files/${filename}`)
  return response.data
}
