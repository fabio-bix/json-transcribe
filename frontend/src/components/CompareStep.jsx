import { useRef, useState, useEffect } from 'react'
import { Upload as UploadIcon, FileJson, Loader2, X, Save, Trash2 } from 'lucide-react'
import Dialog from './Dialog'
import './CompareStep.css'

const STORAGE_KEY = 'compare_base_file'

const CompareStep = ({ onCompare, loading }) => {
  const file1InputRef = useRef(null)
  const file2InputRef = useRef(null)
  const [dragActive1, setDragActive1] = useState(false)
  const [dragActive2, setDragActive2] = useState(false)
  const [file1, setFile1] = useState(null)
  const [file2, setFile2] = useState(null)
  const [savedBaseFile, setSavedBaseFile] = useState(null)
  const [usingSavedFile, setUsingSavedFile] = useState(false)
  const [dialog, setDialog] = useState({ isOpen: false, title: '', message: '', type: 'info', onConfirm: null, showCancel: false })

  // Carregar arquivo salvo ao montar o componente
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        setSavedBaseFile(parsed)
        setUsingSavedFile(true)
        // Criar um objeto File simulado a partir dos dados salvos
        const blob = new Blob([JSON.stringify(parsed.data, null, 2)], { type: 'application/json' })
        const file = new File([blob], parsed.filename, { type: 'application/json' })
        setFile1(file)
      } catch (err) {
        console.error('Erro ao carregar arquivo salvo:', err)
        localStorage.removeItem(STORAGE_KEY)
      }
    }
  }, [])

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

  const handleFile = async (file, setFile) => {
    if (!file.name.endsWith('.json')) {
      setDialog({
        isOpen: true,
        title: 'Formato Inválido',
        message: 'Por favor, selecione um arquivo JSON',
        type: 'error',
        onConfirm: null,
        showCancel: false
      })
      return
    }
    setFile(file)
    
    // Se for o arquivo 1 e não estiver usando arquivo salvo, permitir salvar
    if (setFile === setFile1 && !usingSavedFile) {
      // Ler o conteúdo do arquivo para salvar
      const reader = new FileReader()
      reader.onload = async (e) => {
        try {
          const data = JSON.parse(e.target.result)
          // Não salvar automaticamente, apenas permitir que o usuário salve
        } catch (err) {
          console.error('Erro ao ler arquivo:', err)
        }
      }
      reader.readAsText(file)
    }
  }

  const removeFile = (setFile) => {
    setFile(null)
    if (setFile === setFile1) {
      setUsingSavedFile(false)
    }
  }

  const saveBaseFile = async () => {
    if (!file1) return
    
    try {
      const reader = new FileReader()
      reader.onload = async (e) => {
        try {
          const data = JSON.parse(e.target.result)
          const fileData = {
            filename: file1.name,
            data: data,
            savedAt: new Date().toISOString()
          }
          localStorage.setItem(STORAGE_KEY, JSON.stringify(fileData))
          setSavedBaseFile(fileData)
          setUsingSavedFile(true)
          setDialog({
            isOpen: true,
            title: 'Sucesso',
            message: 'Arquivo base salvo com sucesso! Você pode reutilizá-lo em comparações futuras.',
            type: 'success',
            onConfirm: null,
            showCancel: false
          })
        } catch (err) {
          setDialog({
            isOpen: true,
            title: 'Erro',
            message: 'Erro ao salvar arquivo: ' + err.message,
            type: 'error',
            onConfirm: null,
            showCancel: false
          })
        }
      }
      reader.readAsText(file1)
    } catch (err) {
      setDialog({
        isOpen: true,
        title: 'Erro',
        message: 'Erro ao ler arquivo: ' + err.message,
        type: 'error',
        onConfirm: null,
        showCancel: false
      })
    }
  }

  const removeSavedBaseFile = () => {
    setDialog({
      isOpen: true,
      title: 'Confirmar Remoção',
      message: 'Deseja remover o arquivo base salvo?',
      type: 'warning',
      onConfirm: () => {
        localStorage.removeItem(STORAGE_KEY)
        setSavedBaseFile(null)
        setUsingSavedFile(false)
        setFile1(null)
      },
      showCancel: true,
      confirmText: 'Remover',
      cancelText: 'Cancelar'
    })
  }

  const useSavedFile = () => {
    if (savedBaseFile) {
      const blob = new Blob([JSON.stringify(savedBaseFile.data, null, 2)], { type: 'application/json' })
      const file = new File([blob], savedBaseFile.filename, { type: 'application/json' })
      setFile1(file)
      setUsingSavedFile(true)
    }
  }

  const handleCompare = () => {
    if (!file1 || !file2) {
      setDialog({
        isOpen: true,
        title: 'Arquivos Necessários',
        message: 'Por favor, faça upload de ambos os arquivos JSON',
        type: 'warning',
        onConfirm: null,
        showCancel: false
      })
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
        {savedBaseFile && (
          <div className="saved-file-notice">
            <FileJson size={16} />
            <span>Arquivo base salvo: <strong>{savedBaseFile.filename}</strong></span>
            {!usingSavedFile && (
              <button className="btn-use-saved" onClick={useSavedFile}>
                Usar arquivo salvo
              </button>
            )}
          </div>
        )}
      </div>

      <div className="compare-uploads">
        {/* Arquivo 1 */}
        <div className="compare-upload-item">
          <div className="upload-item-header">
            <h3>Arquivo 1 (Base)</h3>
            {file1 && !usingSavedFile && (
              <button className="btn-save-base" onClick={saveBaseFile} title="Salvar como arquivo base">
                <Save size={16} />
                Salvar
              </button>
            )}
            {savedBaseFile && usingSavedFile && (
              <button className="btn-remove-saved" onClick={removeSavedBaseFile} title="Remover arquivo base salvo">
                <Trash2 size={16} />
                Remover
              </button>
            )}
          </div>
          <div
            className={`upload-area ${dragActive1 ? 'drag-active' : ''} ${loading ? 'loading' : ''} ${file1 ? 'has-file' : ''} ${usingSavedFile ? 'using-saved' : ''}`}
            onDragEnter={(e) => handleDrag(e, setDragActive1)}
            onDragLeave={(e) => handleDrag(e, setDragActive1)}
            onDragOver={(e) => handleDrag(e, setDragActive1)}
            onDrop={(e) => {
              e.preventDefault()
              e.stopPropagation()
              setDragActive1(false)
              if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleFile(e.dataTransfer.files[0], setFile1)
                setUsingSavedFile(false)
              }
            }}
            onClick={() => !loading && !file1 && file1InputRef.current?.click()}
          >
            <input
              ref={file1InputRef}
              type="file"
              accept=".json"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleFile(e.target.files[0], setFile1)
                  setUsingSavedFile(false)
                }
              }}
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
                  {usingSavedFile && (
                    <p className="file-saved-badge">✓ Arquivo base salvo</p>
                  )}
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
                {savedBaseFile && (
                  <p className="upload-hint-saved">
                    💡 Você tem um arquivo base salvo. Use-o para comparar com múltiplos arquivos!
                  </p>
                )}
              </>
            )}
          </div>
        </div>

        {/* Arquivo 2 */}
        <div className="compare-upload-item">
          <div className="upload-item-header">
            <h3>Arquivo 2</h3>
          </div>
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

      <Dialog
        isOpen={dialog.isOpen}
        onClose={() => setDialog({ ...dialog, isOpen: false })}
        title={dialog.title}
        message={dialog.message}
        type={dialog.type}
        onConfirm={dialog.onConfirm}
        confirmText={dialog.confirmText || 'OK'}
        cancelText={dialog.cancelText || 'Cancelar'}
        showCancel={dialog.showCancel}
      />
    </div>
  )
}

export default CompareStep


