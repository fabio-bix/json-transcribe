import { useRef, useState } from 'react'
import { Upload as UploadIcon, FileJson, Loader2, X } from 'lucide-react'
import './CompareStep.css'

const CompareStep = ({ onCompare, loading }) => {
  const file1InputRef = useRef(null)
  const file2InputRef = useRef(null)
  const [dragActive1, setDragActive1] = useState(false)
  const [dragActive2, setDragActive2] = useState(false)
  const [file1, setFile1] = useState(null)
  const [file2, setFile2] = useState(null)

  const handleDrag = (e, setDragActive) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e, setDragActive, setFile) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0], setFile)
    }
  }

  const handleFileInput = (e, setFile) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0], setFile)
    }
  }

  const handleFile = (file, setFile) => {
    if (!file.name.endsWith('.json')) {
      alert('Por favor, selecione um arquivo JSON')
      return
    }
    setFile(file)
  }

  const removeFile = (setFile) => {
    setFile(null)
  }

  const handleCompare = () => {
    if (!file1 || !file2) {
      alert('Por favor, faça upload de ambos os arquivos JSON')
      return
    }
    onCompare(file1, file2)
  }

  return (
    <div className="compare-step">
      <div className="compare-header">
        <FileJson size={48} className="compare-icon" />
        <h2>Comparar Arquivos JSON</h2>
        <p>Faça upload de dois arquivos JSON para comparar as diferenças</p>
      </div>

      <div className="compare-uploads">
        {/* Arquivo 1 */}
        <div className="compare-upload-item">
          <h3>Arquivo 1</h3>
          <div
            className={`upload-area ${dragActive1 ? 'drag-active' : ''} ${loading ? 'loading' : ''} ${file1 ? 'has-file' : ''}`}
            onDragEnter={(e) => handleDrag(e, setDragActive1)}
            onDragLeave={(e) => handleDrag(e, setDragActive1)}
            onDragOver={(e) => handleDrag(e, setDragActive1)}
            onDrop={(e) => handleDrop(e, setDragActive1, setFile1)}
            onClick={() => !loading && !file1 && file1InputRef.current?.click()}
          >
            <input
              ref={file1InputRef}
              type="file"
              accept=".json"
              onChange={(e) => handleFileInput(e, setFile1)}
              style={{ display: 'none' }}
              disabled={loading || !!file1}
            />
            
            {loading ? (
              <div className="upload-loading">
                <Loader2 size={32} className="spinner" />
                <p>Processando...</p>
              </div>
            ) : file1 ? (
              <div className="file-info">
                <FileJson size={32} />
                <div className="file-details">
                  <p className="file-name">{file1.name}</p>
                  <p className="file-size">{(file1.size / 1024).toFixed(2)} KB</p>
                </div>
                <button
                  className="remove-file-btn"
                  onClick={(e) => {
                    e.stopPropagation()
                    removeFile(setFile1)
                  }}
                >
                  <X size={20} />
                </button>
              </div>
            ) : (
              <>
                <UploadIcon size={48} />
                <p className="upload-text">
                  <strong>Clique para selecionar</strong> ou arraste o arquivo aqui
                </p>
                <p className="upload-hint">Apenas arquivos .json são aceitos</p>
              </>
            )}
          </div>
        </div>

        {/* Arquivo 2 */}
        <div className="compare-upload-item">
          <h3>Arquivo 2</h3>
          <div
            className={`upload-area ${dragActive2 ? 'drag-active' : ''} ${loading ? 'loading' : ''} ${file2 ? 'has-file' : ''}`}
            onDragEnter={(e) => handleDrag(e, setDragActive2)}
            onDragLeave={(e) => handleDrag(e, setDragActive2)}
            onDragOver={(e) => handleDrag(e, setDragActive2)}
            onDrop={(e) => handleDrop(e, setDragActive2, setFile2)}
            onClick={() => !loading && !file2 && file2InputRef.current?.click()}
          >
            <input
              ref={file2InputRef}
              type="file"
              accept=".json"
              onChange={(e) => handleFileInput(e, setFile2)}
              style={{ display: 'none' }}
              disabled={loading || !!file2}
            />
            
            {loading ? (
              <div className="upload-loading">
                <Loader2 size={32} className="spinner" />
                <p>Processando...</p>
              </div>
            ) : file2 ? (
              <div className="file-info">
                <FileJson size={32} />
                <div className="file-details">
                  <p className="file-name">{file2.name}</p>
                  <p className="file-size">{(file2.size / 1024).toFixed(2)} KB</p>
                </div>
                <button
                  className="remove-file-btn"
                  onClick={(e) => {
                    e.stopPropagation()
                    removeFile(setFile2)
                  }}
                >
                  <X size={20} />
                </button>
              </div>
            ) : (
              <>
                <UploadIcon size={48} />
                <p className="upload-text">
                  <strong>Clique para selecionar</strong> ou arraste o arquivo aqui
                </p>
                <p className="upload-hint">Apenas arquivos .json são aceitos</p>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="compare-actions">
        <button
          className="btn btn-primary"
          onClick={handleCompare}
          disabled={!file1 || !file2 || loading}
        >
          Comparar Arquivos
        </button>
      </div>
    </div>
  )
}

export default CompareStep


