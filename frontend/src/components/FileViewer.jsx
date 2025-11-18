import { useState } from 'react'
import { X, Download, Copy, Check } from 'lucide-react'
import { downloadTranslatedFile } from '../services/api'
import './FileViewer.css'

const FileViewer = ({ data, filename, onClose }) => {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    const jsonString = JSON.stringify(data, null, 2)
    navigator.clipboard.writeText(jsonString)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = async () => {
    try {
      await downloadTranslatedFile(filename)
    } catch (err) {
      alert(`Erro ao baixar arquivo: ${err.message}`)
    }
  }

  return (
    <div className="file-viewer-overlay" onClick={onClose}>
      <div className="file-viewer" onClick={(e) => e.stopPropagation()}>
        <div className="viewer-header">
          <div>
            <h3>{filename}</h3>
            <p>{Object.keys(data).length} chaves principais</p>
          </div>
          <div className="viewer-actions">
            <button className="btn-icon" onClick={handleCopy} title="Copiar JSON">
              {copied ? <Check size={20} /> : <Copy size={20} />}
            </button>
            <button className="btn-icon" onClick={handleDownload} title="Baixar">
              <Download size={20} />
            </button>
            <button className="btn-icon" onClick={onClose} title="Fechar">
              <X size={20} />
            </button>
          </div>
        </div>
        <div className="viewer-content">
          <pre className="json-viewer">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  )
}

export default FileViewer

