import { useState } from 'react'
import { Upload, FileCheck, Settings, Play, Loader2, CheckCircle2, AlertCircle, Download, FolderOpen, GitCompare } from 'lucide-react'
import './styles/App.css'
import UploadStep from './components/UploadStep'
import ValidationStep from './components/ValidationStep'
import ConfigStep from './components/ConfigStep'
import EstimateStep from './components/EstimateStep'
import ProgressStep from './components/ProgressStep'
import ResultStep from './components/ResultStep'
import FilesList from './components/FilesList'
import FileViewer from './components/FileViewer'
import CompareStep from './components/CompareStep'
import CompareView from './components/CompareView'
import { uploadJSON, estimateTranslation, startTranslation, getJobStatus, getJobResult, saveJobResult } from './services/api'
import { saveFileToCache, loadFileFromCache, removeFileFromCache, clearAllCache } from './utils/fileCache'

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
  // Estados para comparação
  const [compareFile1, setCompareFile1] = useState(null)
  const [compareFiles2, setCompareFiles2] = useState([])
  const [compareData1, setCompareData1] = useState(null)
  const [compareFile1Name, setCompareFile1Name] = useState(null)
  const [compareFile2Names, setCompareFile2Names] = useState([])
  const [currentFileIndex, setCurrentFileIndex] = useState(0)
  const [currentFile2Data, setCurrentFile2Data] = useState(null) // Apenas o arquivo atual em memória
  const [loadingFile, setLoadingFile] = useState(false)
  const [fileCacheIds, setFileCacheIds] = useState([]) // IDs dos arquivos no cache

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

  const handleCompare = async (file1, files2) => {
    setLoading(true)
    setError(null)
    try {
      // Limpar cache anterior se existir
      await clearAllCache()
      
      // Fazer upload e parse do arquivo base
      const response1 = await uploadJSON(file1)
      setCompareData1(response1.data)
      setCompareFile1Name(response1.filename)
      setCompareFile1(file1)
      
      // Processar múltiplos arquivos e salvar no cache
      const filesArray = Array.isArray(files2) ? files2 : [files2]
      const namesList = []
      const cacheIds = []
      
      for (let i = 0; i < filesArray.length; i++) {
        const file = filesArray[i]
        const response = await uploadJSON(file)
        const fileId = `file2_${Date.now()}_${i}_${Math.random().toString(36).substr(2, 9)}`
        
        // Salvar no cache
        await saveFileToCache(fileId, response.data, response.filename)
        
        namesList.push(response.filename)
        cacheIds.push(fileId)
      }
      
      setCompareFile2Names(namesList)
      setFileCacheIds(cacheIds)
      setCompareFiles2(filesArray)
      setCurrentFileIndex(0)
      
      // Carregar apenas o primeiro arquivo em memória
      if (cacheIds.length > 0) {
        const firstFileData = await loadFileFromCache(cacheIds[0])
        setCurrentFile2Data(firstFileData)
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Erro ao processar arquivos')
    } finally {
      setLoading(false)
    }
  }

  const handleBackFromCompare = async () => {
    // Limpar cache ao sair
    await clearAllCache()
    
    setCompareFile1(null)
    setCompareFiles2([])
    setCompareData1(null)
    setCompareFile2Names([])
    setCurrentFileIndex(0)
    setCurrentFile2Data(null)
    setFileCacheIds([])
    setError(null)
  }

  const loadFileAtIndex = async (index) => {
    if (index < 0 || index >= fileCacheIds.length) return
    
    setLoadingFile(true)
    try {
      const fileId = fileCacheIds[index]
      const fileData = await loadFileFromCache(fileId)
      setCurrentFile2Data(fileData)
    } catch (err) {
      console.error('Erro ao carregar arquivo do cache:', err)
      setError('Erro ao carregar arquivo do cache')
    } finally {
      setLoadingFile(false)
    }
  }

  const handleNextFile = async () => {
    if (currentFileIndex < fileCacheIds.length - 1) {
      const newIndex = currentFileIndex + 1
      setCurrentFileIndex(newIndex)
      await loadFileAtIndex(newIndex)
    }
  }

  const handlePreviousFile = async () => {
    if (currentFileIndex > 0) {
      const newIndex = currentFileIndex - 1
      setCurrentFileIndex(newIndex)
      await loadFileAtIndex(newIndex)
    }
  }

  const handleSelectFile = async (index) => {
    // Prevenir múltiplas chamadas simultâneas
    if (loadingFile) return
    
    if (index >= 0 && index < fileCacheIds.length && index !== currentFileIndex) {
      setCurrentFileIndex(index)
      await loadFileAtIndex(index)
    }
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
                className={`nav-btn ${page === 'compare' ? 'active' : ''}`}
                onClick={() => {
                  setPage('compare')
                  handleBackFromCompare()
                }}
              >
                <GitCompare size={20} />
                Comparar JSONs
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
          ) : page === 'compare' ? (
            <>
              {error && (
                <div className="alert error">
                  <AlertCircle size={20} />
                  <span>{error}</span>
                </div>
              )}

              {compareData1 && currentFile2Data && fileCacheIds.length > 0 ? (
                <CompareView
                  file1Data={compareData1}
                  file2Data={currentFile2Data}
                  file1Name={compareFile1Name}
                  file2Name={compareFile2Names[currentFileIndex]}
                  currentIndex={currentFileIndex}
                  totalFiles={fileCacheIds.length}
                  fileNames={compareFile2Names}
                  loadingFile={loadingFile}
                  onSelectFile={handleSelectFile}
                  onBack={handleBackFromCompare}
                />
              ) : (
                <CompareStep
                  onCompare={handleCompare}
                  loading={loading}
                />
              )}
            </>
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

