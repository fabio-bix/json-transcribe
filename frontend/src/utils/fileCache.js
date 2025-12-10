// Utilitário para cache de arquivos processados
// Usa IndexedDB para arquivos grandes e localStorage como fallback

const CACHE_PREFIX = 'compare_file_cache_'
const CACHE_METADATA_KEY = 'compare_cache_metadata'
const MAX_LOCALSTORAGE_SIZE = 5 * 1024 * 1024 // 5MB - limite aproximado do localStorage

// Verificar se IndexedDB está disponível
const isIndexedDBAvailable = () => {
  return typeof indexedDB !== 'undefined'
}

// Obter tamanho aproximado de um objeto JSON em bytes
const getObjectSize = (obj) => {
  return new Blob([JSON.stringify(obj)]).size
}

// Salvar no IndexedDB
const saveToIndexedDB = async (key, data) => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('CompareFileCache', 1)
    
    request.onerror = () => reject(request.error)
    request.onsuccess = () => {
      const db = request.result
      const transaction = db.transaction(['files'], 'readwrite')
      const store = transaction.objectStore('files')
      const putRequest = store.put({ key, data, timestamp: Date.now() })
      putRequest.onsuccess = () => resolve()
      putRequest.onerror = () => reject(putRequest.error)
    }
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result
      if (!db.objectStoreNames.contains('files')) {
        db.createObjectStore('files', { keyPath: 'key' })
      }
    }
  })
}

// Ler do IndexedDB
const readFromIndexedDB = async (key) => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('CompareFileCache', 1)
    
    request.onerror = () => reject(request.error)
    request.onsuccess = () => {
      const db = request.result
      const transaction = db.transaction(['files'], 'readonly')
      const store = transaction.objectStore('files')
      const getRequest = store.get(key)
      getRequest.onsuccess = () => {
        if (getRequest.result) {
          resolve(getRequest.result.data)
        } else {
          resolve(null)
        }
      }
      getRequest.onerror = () => reject(getRequest.error)
    }
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result
      if (!db.objectStoreNames.contains('files')) {
        db.createObjectStore('files', { keyPath: 'key' })
      }
    }
  })
}

// Remover do IndexedDB
const removeFromIndexedDB = async (key) => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('CompareFileCache', 1)
    
    request.onerror = () => reject(request.error)
    request.onsuccess = () => {
      const db = request.result
      const transaction = db.transaction(['files'], 'readwrite')
      const store = transaction.objectStore('files')
      const deleteRequest = store.delete(key)
      deleteRequest.onsuccess = () => resolve()
      deleteRequest.onerror = () => reject(deleteRequest.error)
    }
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result
      if (!db.objectStoreNames.contains('files')) {
        db.createObjectStore('files', { keyPath: 'key' })
      }
    }
  })
}

// Salvar arquivo no cache
export const saveFileToCache = async (fileId, data, filename) => {
  const key = `${CACHE_PREFIX}${fileId}`
  const size = getObjectSize(data)
  
  try {
    // Se IndexedDB está disponível ou arquivo é grande, usar IndexedDB
    if (isIndexedDBAvailable() || size > MAX_LOCALSTORAGE_SIZE) {
      if (isIndexedDBAvailable()) {
        await saveToIndexedDB(key, { data, filename })
      } else {
        // Fallback: comprimir e salvar no localStorage
        const compressed = JSON.stringify({ data, filename })
        if (compressed.length < MAX_LOCALSTORAGE_SIZE) {
          localStorage.setItem(key, compressed)
        } else {
          console.warn('Arquivo muito grande para cache local')
          return false
        }
      }
    } else {
      // Salvar no localStorage
      localStorage.setItem(key, JSON.stringify({ data, filename }))
    }
    
    // Atualizar metadata
    const metadata = getCacheMetadata()
    metadata[fileId] = { filename, size, timestamp: Date.now() }
    saveCacheMetadata(metadata)
    
    return true
  } catch (error) {
    console.error('Erro ao salvar no cache:', error)
    return false
  }
}

// Carregar arquivo do cache
export const loadFileFromCache = async (fileId) => {
  const key = `${CACHE_PREFIX}${fileId}`
  
  try {
    let cached = null
    
    if (isIndexedDBAvailable()) {
      cached = await readFromIndexedDB(key)
    }
    
    // Se não encontrou no IndexedDB, tentar localStorage
    if (!cached) {
      const stored = localStorage.getItem(key)
      if (stored) {
        cached = JSON.parse(stored)
      }
    }
    
    return cached ? cached.data : null
  } catch (error) {
    console.error('Erro ao carregar do cache:', error)
    return null
  }
}

// Remover arquivo do cache
export const removeFileFromCache = async (fileId) => {
  const key = `${CACHE_PREFIX}${fileId}`
  
  try {
    if (isIndexedDBAvailable()) {
      await removeFromIndexedDB(key)
    } else {
      localStorage.removeItem(key)
    }
    
    // Atualizar metadata
    const metadata = getCacheMetadata()
    delete metadata[fileId]
    saveCacheMetadata(metadata)
  } catch (error) {
    console.error('Erro ao remover do cache:', error)
  }
}

// Limpar todo o cache
export const clearAllCache = async () => {
  try {
    const metadata = getCacheMetadata()
    const fileIds = Object.keys(metadata)
    
    for (const fileId of fileIds) {
      await removeFileFromCache(fileId)
    }
    
    // Limpar IndexedDB completamente se disponível
    if (isIndexedDBAvailable()) {
      const request = indexedDB.deleteDatabase('CompareFileCache')
      await new Promise((resolve, reject) => {
        request.onsuccess = () => resolve()
        request.onerror = () => reject(request.error)
      })
    }
    
    saveCacheMetadata({})
  } catch (error) {
    console.error('Erro ao limpar cache:', error)
  }
}

// Obter metadata do cache
const getCacheMetadata = () => {
  try {
    const stored = localStorage.getItem(CACHE_METADATA_KEY)
    return stored ? JSON.parse(stored) : {}
  } catch {
    return {}
  }
}

// Salvar metadata do cache
const saveCacheMetadata = (metadata) => {
  try {
    localStorage.setItem(CACHE_METADATA_KEY, JSON.stringify(metadata))
  } catch (error) {
    console.error('Erro ao salvar metadata:', error)
  }
}

// Obter informações do cache
export const getCacheInfo = () => {
  const metadata = getCacheMetadata()
  const totalFiles = Object.keys(metadata).length
  const totalSize = Object.values(metadata).reduce((sum, info) => sum + (info.size || 0), 0)
  
  return {
    totalFiles,
    totalSize,
    files: Object.entries(metadata).map(([id, info]) => ({
      id,
      filename: info.filename,
      size: info.size,
      timestamp: info.timestamp
    }))
  }
}

