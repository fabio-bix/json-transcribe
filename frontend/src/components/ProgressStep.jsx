import { useEffect, useState } from 'react'
import { Loader2, CheckCircle2, Clock, DollarSign, Globe, Zap, TrendingUp } from 'lucide-react'
import './ProgressStep.css'

const ProgressStep = ({ jobStatus, config }) => {
  const [progressBarWidth, setProgressBarWidth] = useState(0)
  const [elapsedTime, setElapsedTime] = useState(0)

  useEffect(() => {
    if (jobStatus) {
      setProgressBarWidth(jobStatus.progress * 100)
    }
  }, [jobStatus])

  useEffect(() => {
    if (!jobStatus || jobStatus.status !== 'processing') {
      if (jobStatus?.elapsed_seconds !== null && jobStatus?.elapsed_seconds !== undefined) {
        setElapsedTime(jobStatus.elapsed_seconds)
      }
      return
    }

    if (jobStatus.elapsed_seconds !== null && jobStatus.elapsed_seconds !== undefined) {
      setElapsedTime(jobStatus.elapsed_seconds)
    }

    const interval = setInterval(() => {
      if (jobStatus.elapsed_seconds !== null && jobStatus.elapsed_seconds !== undefined) {
        setElapsedTime(jobStatus.elapsed_seconds)
      } else {
        setElapsedTime(prev => prev + 1)
      }
    }, 1000)

    return () => clearInterval(interval)
  }, [jobStatus])

  const formatTime = (seconds) => {
    if (!seconds && seconds !== 0) return 'calculando...'
    if (seconds < 60) return `${Math.round(seconds)}s`
    if (seconds < 3600) {
      const min = Math.floor(seconds / 60)
      const sec = Math.round(seconds % 60)
      return `${min}m ${sec}s`
    }
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  const getLanguageName = (code) => {
    const languages = {
      "es": "Espanhol", "pt": "Português", "fr": "Francês", "de": "Alemão",
      "it": "Italiano", "nl": "Holandês", "pl": "Polonês", "sv": "Sueco",
      "da": "Dinamarquês", "no": "Norueguês", "fi": "Finlandês", "cs": "Tcheco",
      "hu": "Húngaro", "ro": "Romeno", "hr": "Croata", "sr": "Sérvio (Latinizado)",
      "tr": "Turco", "id": "Indonésio", "tl": "Filipino (Tagalog)", "ms": "Malaio",
    }
    return languages[code] || code
  }

  if (!jobStatus) {
    return (
      <div className="progress-step">
        <Loader2 size={48} className="spinner" />
        <p>Carregando status...</p>
      </div>
    )
  }

  const targetLang = jobStatus.target_language || (config ? getLanguageName(config.targetLanguage) : '')
  const model = jobStatus.model || (config ? config.model : '')
  const elapsed = jobStatus.elapsed_seconds !== null && jobStatus.elapsed_seconds !== undefined 
    ? jobStatus.elapsed_seconds 
    : elapsedTime

  return (
    <div className="progress-step">
      <div className="progress-header">
        <Loader2 size={48} className="spinner progress-icon" />
        <h2>Traduzindo para {targetLang || 'idioma selecionado'}...</h2>
        <p>Processando seu arquivo JSON</p>
        {model && (
          <div className="translation-info">
            <span className="info-badge">
              <Zap size={16} />
              Modelo: {model}
            </span>
            {targetLang && (
              <span className="info-badge">
                <Globe size={16} />
                {targetLang}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Progress Bar */}
      <div className="progress-container">
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${progressBarWidth}%` }}
          />
        </div>
        <p className="progress-text">
          {Math.round(jobStatus.progress * 100)}% concluído
        </p>
      </div>

      {/* Time Info */}
      <div className="time-info-section">
        <div className="time-card">
          <Clock size={24} />
          <div>
            <p className="time-label">Tempo Decorrido</p>
            <p className="time-value">{formatTime(elapsed)}</p>
          </div>
        </div>
        {jobStatus.estimated_total_seconds && (
          <div className="time-card">
            <TrendingUp size={24} />
            <div>
              <p className="time-label">Tempo Estimado Total</p>
              <p className="time-value">{formatTime(jobStatus.estimated_total_seconds)}</p>
            </div>
          </div>
        )}
        {jobStatus.eta_seconds !== null && jobStatus.eta_seconds !== undefined && (
          <div className="time-card highlight">
            <Clock size={24} />
            <div>
              <p className="time-label">Tempo Restante (ETA)</p>
              <p className="time-value">{formatTime(jobStatus.eta_seconds)}</p>
            </div>
          </div>
        )}
      </div>

      {/* Stats Grid */}
      <div className="progress-stats">
        <div className="stat-card">
          <CheckCircle2 size={20} />
          <div>
            <p className="stat-value">
              {jobStatus.translated_strings} / {jobStatus.total_strings}
            </p>
            <p className="stat-label">Strings Traduzidas</p>
            <p className="stat-sublabel">
              {jobStatus.cached_strings > 0 && `${jobStatus.cached_strings} do cache`}
            </p>
          </div>
        </div>

        <div className="stat-card">
          <Clock size={20} />
          <div>
            <p className="stat-value">
              {jobStatus.current_batch} / {jobStatus.total_batches}
            </p>
            <p className="stat-label">Batches Processados</p>
            {jobStatus.total_batches > 0 && (
              <p className="stat-sublabel">
                {Math.round((jobStatus.current_batch / jobStatus.total_batches) * 100)}% dos batches
              </p>
            )}
          </div>
        </div>

        <div className="stat-card">
          <DollarSign size={20} />
          <div>
            <p className="stat-value">${jobStatus.actual_cost.toFixed(6)}</p>
            <p className="stat-label">Custo Atual</p>
            {jobStatus.estimated_cost > 0 && (
              <p className="stat-sublabel">
                Est. total: ${jobStatus.estimated_cost.toFixed(6)}
              </p>
            )}
          </div>
        </div>

        {jobStatus.stats.api_calls > 0 && (
          <div className="stat-card">
            <Zap size={20} />
            <div>
              <p className="stat-value">{jobStatus.stats.api_calls}</p>
              <p className="stat-label">Chamadas API</p>
              {jobStatus.total_batches > 0 && (
                <p className="stat-sublabel">
                  ~{Math.round((jobStatus.stats.api_calls / jobStatus.total_batches) * 100)}% concluído
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Detailed Stats */}
      <div className="detailed-stats">
        <h3>Estatísticas Detalhadas</h3>
        <div className="stats-grid">
          <div className="stat-item">
            <span>Tokens Input:</span>
            <span>{jobStatus.stats.total_prompt_tokens.toLocaleString()}</span>
          </div>
          <div className="stat-item">
            <span>Tokens Output:</span>
            <span>{jobStatus.stats.total_completion_tokens.toLocaleString()}</span>
          </div>
          <div className="stat-item">
            <span>Total Tokens:</span>
            <span>{jobStatus.stats.total_tokens.toLocaleString()}</span>
          </div>
          <div className="stat-item">
            <span>Chamadas API:</span>
            <span>{jobStatus.stats.api_calls}</span>
          </div>
          <div className="stat-item">
            <span>Em Cache:</span>
            <span>{jobStatus.cached_strings}</span>
          </div>
          <div className="stat-item">
            <span>Erros:</span>
            <span>{jobStatus.stats.errors || 0}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProgressStep

