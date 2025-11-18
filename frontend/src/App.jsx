import { useState } from 'react'
import { Upload, FileCheck, Settings, Play, Loader2, CheckCircle2, AlertCircle, Download, FolderOpen } from 'lucide-react'
import './styles/App.css'
import UploadStep from './components/UploadStep'
import ValidationStep from './components/ValidationStep'
import ConfigStep from './components/ConfigStep'
import EstimateStep from './components/EstimateStep'
import ProgressStep from './components/ProgressStep'
import ResultStep from './components/ResultStep'
import FilesList from './components/FilesList'
import FileViewer from './components/FileViewer'
import { uploadJSON, estimateTranslation, startTranslation, getJobStatus, getJobResult, saveJobResult } from './services/api'

function App() {
  const [page, setPage] = useState('translate')
  const [step, setStep] = useState(1)
  const [jsonData, setJsonData] = useState(null)
  const [uploadInfo, setUploadInfo] = useState(null)
  const [config, setConfig] = useState({
    method: 'openai',
    model: 'gpt-4o-mini',
    targetLanguage: 'pt',
    batchSize: 100,
    parallel: 3
  })
  const [estimate, setEstimate] = useState(null)
  const [jobId, setJobId] = useState(null)
  const [jobStatus, setJobStatus] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [viewingFile, setViewingFile] = useState(null)
  const [viewingFilename, setViewingFilename] = useState(null)

  const handleUpload = async (file) => {
    setLoading(true)
    setError(null)
    try {
      const response = await uploadJSON(file)
      setJsonData(response.data)
      setUploadInfo({
        filename: response.filename,
        totalEntries: response.total_entries,
        stringsCount: response.strings_count
      })
      setStep(2)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Erro ao fazer upload')
    } finally {
      setLoading(false)
    }
  }

  const handleEstimate = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await estimateTranslation(jsonData, config)
      setEstimate(response)
      setStep(4)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Erro ao estimar')
    } finally {
      setLoading(false)
    }
  }

  const handleStart = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await startTranslation(jsonData, config)
      setJobId(response.job_id)
      setStep(5)
      pollJobStatus(response.job_id)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Erro ao iniciar tradução')
      setLoading(false)
    }
  }

  const pollJobStatus = async (id) => {
    const interval = setInterval(async () => {
      try {
        const status = await getJobStatus(id)
        setJobStatus(status)
        
        if (status.status === 'completed') {
          clearInterval(interval)
          const resultData = await getJobResult(id)
          setResult(resultData)
          setStep(6)
          setLoading(false)
        } else if (status.status === 'failed') {
          clearInterval(interval)
          setError(status.error_message || 'Tradução falhou')
          setLoading(false)
        }
      } catch (err) {
        clearInterval(interval)
        setError(err.message || 'Erro ao verificar status')
        setLoading(false)
      }
    }, 2000)
  }

  const handleReset = () => {
    setStep(1)
    setJsonData(null)
    setUploadInfo(null)
    setEstimate(null)
    setJobId(null)
    setJobStatus(null)
    setResult(null)
    setError(null)
    setConfig({
      method: 'openai',
      model: 'gpt-4o-mini',
      targetLanguage: 'pt',
      batchSize: 100,
      parallel: 3
    })
  }

  const handleDownload = async () => {
    if (!result || !jobId) return
    
    try {
      await saveJobResult(jobId)
      
      const blob = new Blob([JSON.stringify(result.data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `translated_${config.targetLanguage}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (err) {
      alert(`Erro ao salvar arquivo: ${err.response?.data?.detail || err.message}`)
    }
  }

  const handleViewFile = (data, filename) => {
    setViewingFile(data)
    setViewingFilename(filename)
  }

  const handleCloseViewer = () => {
    setViewingFile(null)
    setViewingFilename(null)
  }

  return (
    <div className="app">
      <header className="header">
        <div className="container">
          <div className="header-main">
            <div>
              <h1>
                <span className="emoji">🌍</span>
                <span className="title-text">JSON Translator</span>
              </h1>
              <p>Traduza seus arquivos JSON com IA ou Google Translate</p>
            </div>
            <nav className="header-nav">
              <button
                className={`nav-btn ${page === 'translate' ? 'active' : ''}`}
                onClick={() => {
                  setPage('translate')
                  handleReset()
                }}
              >
                <Upload size={20} />
                Nova Tradução
              </button>
              <button
                className={`nav-btn ${page === 'files' ? 'active' : ''}`}
                onClick={() => setPage('files')}
              >
                <FolderOpen size={20} />
                Arquivos
              </button>
            </nav>
          </div>
        </div>
      </header>

      <main className="main">
        <div className="container">
          {page === 'files' ? (
            <FilesList
              onViewFile={handleViewFile}
              onBack={() => {
                setPage('translate')
                handleReset()
              }}
            />
          ) : (
            <>
              <div className="steps-indicator">
            <div className={`step-item ${step >= 1 ? 'active' : ''} ${step > 1 ? 'completed' : ''}`}>
              <Upload size={20} />
              <span>Upload</span>
            </div>
            <div className={`step-item ${step >= 2 ? 'active' : ''} ${step > 2 ? 'completed' : ''}`}>
              <FileCheck size={20} />
              <span>Validação</span>
            </div>
            <div className={`step-item ${step >= 3 ? 'active' : ''} ${step > 3 ? 'completed' : ''}`}>
              <Settings size={20} />
              <span>Configuração</span>
            </div>
            <div className={`step-item ${step >= 4 ? 'active' : ''} ${step > 4 ? 'completed' : ''}`}>
              <Play size={20} />
              <span>Tradução</span>
            </div>
            <div className={`step-item ${step >= 5 ? 'active' : ''} ${step > 5 ? 'completed' : ''}`}>
              <Loader2 size={20} />
              <span>Progresso</span>
            </div>
            <div className={`step-item ${step >= 6 ? 'active' : ''}`}>
              <CheckCircle2 size={20} />
              <span>Resultado</span>
            </div>
          </div>

          {error && (
            <div className="alert error">
              <AlertCircle size={20} />
              <span>{error}</span>
            </div>
          )}

          <div className="step-content">
            {step === 1 && (
              <UploadStep 
                onUpload={handleUpload} 
                loading={loading}
              />
            )}

            {step === 2 && uploadInfo && (
              <ValidationStep 
                uploadInfo={uploadInfo}
                onNext={() => setStep(3)}
                onBack={() => setStep(1)}
              />
            )}

            {step === 3 && (
              <ConfigStep 
                config={config}
                onConfigChange={setConfig}
                onNext={handleEstimate}
                onBack={() => setStep(2)}
                loading={loading}
              />
            )}

            {step === 4 && estimate && (
              <EstimateStep 
                estimate={estimate}
                onStart={handleStart}
                onBack={() => setStep(3)}
                loading={loading}
              />
            )}

            {step === 5 && jobStatus && (
              <ProgressStep 
                jobStatus={jobStatus}
                config={config}
              />
            )}

            {step === 6 && result && (
              <ResultStep 
                result={result}
                onDownload={handleDownload}
                onReset={handleReset}
                onViewFiles={() => setPage('files')}
              />
            )}
          </div>
            </>
          )}
        </div>
      </main>

      {viewingFile && (
        <FileViewer
          data={viewingFile}
          filename={viewingFilename}
          onClose={handleCloseViewer}
        />
      )}
    </div>
  )
}

export default App

