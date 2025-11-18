import { useState, useEffect } from 'react'
import { FileJson, Download, Trash2, Eye, RefreshCw, Loader2, Calendar, HardDrive, Globe } from 'lucide-react'
import { listTranslatedFiles, downloadTranslatedFile, deleteTranslatedFile, getTranslatedFile } from '../services/api'
import './FilesList.css'

const FilesList = ({ onViewFile, onBack }) => {
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [deleting, setDeleting] = useState(null)

  const loadFiles = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await listTranslatedFiles()
      setFiles(response.files || [])
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Erro ao carregar arquivos')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadFiles()
  }, [])

  const handleDownload = async (filename) => {
    try {
      await downloadTranslatedFile(filename)
    } catch (err) {
      alert(`Erro ao baixar arquivo: ${err.response?.data?.detail || err.message}`)
    }
  }

  const handleDelete = async (filename) => {
    if (!confirm(`Tem certeza que deseja excluir "${filename}"?`)) {
      return
    }

    setDeleting(filename)
    try {
      await deleteTranslatedFile(filename)
      await loadFiles()
    } catch (err) {
      alert(`Erro ao excluir arquivo: ${err.response?.data?.detail || err.message}`)
    } finally {
      setDeleting(null)
    }
  }

  const handleView = async (filename) => {
    try {
      const response = await getTranslatedFile(filename)
      onViewFile(response.data, filename)
    } catch (err) {
      alert(`Erro ao visualizar arquivo: ${err.response?.data?.detail || err.message}`)
    }
  }

  const formatDate = (timestamp) => {
    const date = new Date(timestamp * 1000)
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const formatSize = (sizeKb) => {
    if (sizeKb < 1024) {
      return `${sizeKb.toFixed(2)} KB`
    }
    return `${(sizeKb / 1024).toFixed(2)} MB`
  }

  return (
    <div className="files-list">
      <div className="files-header">
        <div className="header-content">
          <FileJson size={32} />
          <div>
            <h2>Arquivos Traduzidos</h2>
            <p>Gerencie seus arquivos JSON traduzidos</p>
          </div>
        </div>
        <div className="header-actions">
          <button className="btn btn-secondary" onClick={loadFiles} disabled={loading}>
            <RefreshCw size={20} className={loading ? 'spinner' : ''} />
            Atualizar
          </button>
          {onBack && (
            <button className="btn btn-primary" onClick={onBack}>
              Nova Tradução
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="alert error">
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="loading-state">
          <Loader2 size={48} className="spinner" />
          <p>Carregando arquivos...</p>
        </div>
      ) : files.length === 0 ? (
        <div className="empty-state">
          <FileJson size={64} />
          <h3>Nenhum arquivo traduzido</h3>
          <p>Os arquivos traduzidos aparecerão aqui</p>
          {onBack && (
            <button className="btn btn-primary" onClick={onBack}>
              Criar Primeira Tradução
            </button>
          )}
        </div>
      ) : (
        <div className="files-grid">
          {files.map((file) => (
            <div key={file.filename} className="file-card">
              <div className="file-icon">
                <FileJson size={32} />
              </div>
              <div className="file-info">
                <h3 className="file-name" title={file.filename}>
                  {file.filename}
                </h3>
                <div className="file-meta">
                  {file.language_name && (
                    <div className="meta-item language-badge">
                      <Globe size={16} />
                      <span>{file.language_name}</span>
                    </div>
                  )}
                  <div className="meta-item">
                    <HardDrive size={16} />
                    <span>{formatSize(file.size_kb)}</span>
                  </div>
                  <div className="meta-item">
                    <Calendar size={16} />
                    <span>{formatDate(file.modified)}</span>
                  </div>
                </div>
              </div>
              <div className="file-actions">
                <button
                  className="btn-icon"
                  onClick={() => handleView(file.filename)}
                  title="Visualizar"
                >
                  <Eye size={20} />
                </button>
                <button
                  className="btn-icon"
                  onClick={() => handleDownload(file.filename)}
                  title="Baixar"
                >
                  <Download size={20} />
                </button>
                <button
                  className="btn-icon danger"
                  onClick={() => handleDelete(file.filename)}
                  disabled={deleting === file.filename}
                  title="Excluir"
                >
                  {deleting === file.filename ? (
                    <Loader2 size={20} className="spinner" />
                  ) : (
                    <Trash2 size={20} />
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default FilesList

