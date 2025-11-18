import { CheckCircle2, Download, RotateCcw, FileText, DollarSign, Hash, FolderOpen, AlertTriangle, XCircle } from 'lucide-react'
import './ResultStep.css'

const ResultStep = ({ result, onDownload, onReset, onViewFiles }) => {
  const hasErrors = result.stats.failed_count > 0 || result.stats.errors > 0
  
  return (
    <div className="result-step">
      <div className="result-header">
        {hasErrors ? (
          <AlertTriangle size={64} className="warning-icon" />
        ) : (
          <CheckCircle2 size={64} className="success-icon" />
        )}
        <h2>{hasErrors ? "Tradução Concluída com Avisos" : "Tradução Concluída!"}</h2>
        <p>
          {hasErrors 
            ? `${result.stats.failed_count} chaves precisam de revisão manual`
            : "Seu arquivo foi traduzido com sucesso"
          }
        </p>
      </div>

      {hasErrors && (
        <div className="result-errors">
          <div className="error-header">
            <XCircle size={20} />
            <h3>Chaves com Problemas ({result.stats.failed_count})</h3>
          </div>
          <div className="error-details">
            {result.stats.needs_review_count > 0 && (
              <p className="error-count">
                <strong>{result.stats.needs_review_count}</strong> chaves marcadas como "{result.stats.needs_review_count > 0 ? 'NEEDS_MANUAL_REVIEW' : 'falha'}"
              </p>
            )}
            {result.stats.empty_count > 0 && (
              <p className="error-count">
                <strong>{result.stats.empty_count}</strong> chaves retornaram vazias
              </p>
            )}
            {result.stats.errors > 0 && (
              <p className="error-count">
                <strong>{result.stats.errors}</strong> erros durante a tradução
              </p>
            )}
          </div>
          {result.stats.failed_keys && result.stats.failed_keys.length > 0 && (
            <div className="failed-keys-list">
              <p className="failed-keys-title">Chaves com problemas:</p>
              <div className="failed-keys-grid">
                {result.stats.failed_keys.map((key, idx) => (
                  <span key={idx} className="failed-key-badge">{key}</span>
                ))}
                {result.stats.failed_count > result.stats.failed_keys.length && (
                  <span className="failed-key-badge more">
                    +{result.stats.failed_count - result.stats.failed_keys.length} mais...
                  </span>
                )}
              </div>
            </div>
          )}
          {result.error_message && (
            <div className="error-message">
              <strong>Detalhes:</strong> {result.error_message}
            </div>
          )}
        </div>
      )}

      <div className="result-stats">
        <div className="result-card">
          <FileText size={24} />
          <div>
            <p className="result-label">Total Traduzidas</p>
            <p className="result-value">
              {result.stats.translated + result.stats.cached} / {result.stats.total_strings}
            </p>
            <p className="result-sublabel">
              {result.stats.translated} novas + {result.stats.cached} do cache
            </p>
          </div>
        </div>

        <div className="result-card">
          <Hash size={24} />
          <div>
            <p className="result-label">Traduzidas Agora</p>
            <p className="result-value">{result.stats.translated}</p>
            <p className="result-sublabel">Nesta execução</p>
          </div>
        </div>

        <div className="result-card">
          <Hash size={24} />
          <div>
            <p className="result-label">Do Cache</p>
            <p className="result-value">{result.stats.cached}</p>
            <p className="result-sublabel">Já traduzidas antes</p>
          </div>
        </div>

        <div className="result-card">
          <Hash size={24} />
          <div>
            <p className="result-label">Total de Strings</p>
            <p className="result-value">{result.stats.total_strings}</p>
            <p className="result-sublabel">No arquivo JSON</p>
          </div>
        </div>

        {hasErrors && (
          <div className="result-card error">
            <XCircle size={24} />
            <div>
              <p className="result-label">Chaves com Problemas</p>
              <p className="result-value">{result.stats.failed_count}</p>
            </div>
          </div>
        )}

        <div className="result-card highlight">
          <DollarSign size={24} />
          <div>
            <p className="result-label">Custo Total</p>
            <p className="result-value">${result.stats.cost_usd.toFixed(6)}</p>
          </div>
        </div>

        <div className="result-card">
          <Hash size={24} />
          <div>
            <p className="result-label">Total de Tokens</p>
            <p className="result-value">{result.stats.tokens.toLocaleString()}</p>
          </div>
        </div>
      </div>

      <div className="result-actions">
        <button className="btn btn-success" onClick={onDownload}>
          <Download size={20} />
          Baixar JSON Traduzido
        </button>
        {onViewFiles && (
          <button className="btn btn-secondary" onClick={onViewFiles}>
            <FolderOpen size={20} />
            Ver Arquivos
          </button>
        )}
        <button className="btn btn-secondary" onClick={onReset}>
          <RotateCcw size={20} />
          Nova Tradução
        </button>
      </div>
    </div>
  )
}

export default ResultStep

