import { CheckCircle2, FileText, Hash } from 'lucide-react'
import './ValidationStep.css'

const ValidationStep = ({ uploadInfo, onNext, onBack }) => {
  return (
    <div className="validation-step">
      <div className="validation-header">
        <CheckCircle2 size={48} className="success-icon" />
        <h2>Arquivo Validado com Sucesso!</h2>
        <p>O arquivo JSON foi carregado e validado corretamente</p>
      </div>

      <div className="validation-info">
        <div className="info-card">
          <FileText size={24} />
          <div>
            <p className="info-label">Arquivo</p>
            <p className="info-value">{uploadInfo.filename}</p>
          </div>
        </div>

        <div className="info-card">
          <Hash size={24} />
          <div>
            <p className="info-label">Total de Entradas</p>
            <p className="info-value">{uploadInfo.totalEntries.toLocaleString()}</p>
          </div>
        </div>

        <div className="info-card highlight">
          <Hash size={24} />
          <div>
            <p className="info-label">Strings para Traduzir</p>
            <p className="info-value">{uploadInfo.stringsCount.toLocaleString()}</p>
          </div>
        </div>
      </div>

      <div className="btn-group">
        <button className="btn btn-secondary" onClick={onBack}>
          Voltar
        </button>
        <button className="btn btn-primary" onClick={onNext}>
          Continuar
        </button>
      </div>
    </div>
  )
}

export default ValidationStep

