import { DollarSign, Clock, FileText, TrendingUp } from 'lucide-react'
import './EstimateStep.css'

const EstimateStep = ({ estimate, onStart, onBack, loading }) => {
  const formatTime = (seconds) => {
    if (seconds < 60) return `${seconds}s`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  return (
    <div className="estimate-step">
      <div className="estimate-header">
        <TrendingUp size={48} className="estimate-icon" />
        <h2>Estimativa de Custo e Tempo</h2>
        <p>Revise a estimativa antes de iniciar a tradução</p>
      </div>

      <div className="estimate-grid">
        <div className="estimate-card">
          <FileText size={24} />
          <div>
            <p className="estimate-label">Strings para Traduzir</p>
            <p className="estimate-value">{estimate.total_strings.toLocaleString()}</p>
          </div>
        </div>

        <div className="estimate-card">
          <TrendingUp size={24} />
          <div>
            <p className="estimate-label">Batches Estimados</p>
            <p className="estimate-value">{estimate.estimated_batches}</p>
          </div>
        </div>

        <div className="estimate-card highlight cost">
          <DollarSign size={24} />
          <div>
            <p className="estimate-label">Custo Estimado</p>
            <p className="estimate-value">${estimate.estimated_cost_usd.toFixed(6)}</p>
          </div>
        </div>

        <div className="estimate-card highlight time">
          <Clock size={24} />
          <div>
            <p className="estimate-label">Tempo Estimado</p>
            <p className="estimate-value">{formatTime(estimate.estimated_time_seconds)}</p>
          </div>
        </div>
      </div>

      <div className="estimate-details">
        <h3>Detalhes da Estimativa</h3>
        <div className="details-grid">
          <div className="detail-item">
            <span className="detail-label">Modelo:</span>
            <span className="detail-value">{estimate.model}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Batch Size:</span>
            <span className="detail-value">{estimate.batch_size}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Batches Paralelos:</span>
            <span className="detail-value">{estimate.parallel}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Tokens Input (est.):</span>
            <span className="detail-value">{estimate.estimated_tokens_input.toLocaleString()}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Tokens Output (est.):</span>
            <span className="detail-value">{estimate.estimated_tokens_output.toLocaleString()}</span>
          </div>
        </div>
      </div>

      <div className="btn-group">
        <button className="btn btn-secondary" onClick={onBack} disabled={loading}>
          Voltar
        </button>
        <button className="btn btn-success" onClick={onStart} disabled={loading}>
          {loading ? 'Iniciando...' : 'Iniciar Tradução'}
        </button>
      </div>
    </div>
  )
}

export default EstimateStep

