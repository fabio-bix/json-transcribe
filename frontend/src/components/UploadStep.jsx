import { useRef, useState } from 'react'
import { Upload as UploadIcon, FileJson, Loader2 } from 'lucide-react'
import './UploadStep.css'

const UploadStep = ({ onUpload, loading }) => {
  const fileInputRef = useRef(null)
  const [dragActive, setDragActive] = useState(false)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = (file) => {
    if (!file.name.endsWith('.json')) {
      alert('Por favor, selecione um arquivo JSON')
      return
    }
    onUpload(file)
  }

  return (
    <div className="upload-step">
      <div className="upload-header">
        <FileJson size={48} className="upload-icon" />
        <h2>Upload do Arquivo JSON</h2>
        <p>Selecione ou arraste um arquivo JSON para traduzir</p>
      </div>

      <div
        className={`upload-area ${dragActive ? 'drag-active' : ''} ${loading ? 'loading' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !loading && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          onChange={handleFileInput}
          style={{ display: 'none' }}
          disabled={loading}
        />
        
        {loading ? (
          <div className="upload-loading">
            <Loader2 size={48} className="spinner" />
            <p>Processando arquivo...</p>
          </div>
        ) : (
          <>
            <UploadIcon size={64} />
            <p className="upload-text">
              <strong>Clique para selecionar</strong> ou arraste o arquivo aqui
            </p>
            <p className="upload-hint">Apenas arquivos .json são aceitos</p>
          </>
        )}
      </div>
    </div>
  )
}

export default UploadStep

