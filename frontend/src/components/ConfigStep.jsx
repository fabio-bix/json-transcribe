import { useState, useEffect } from 'react'
import { Settings, Loader2 } from 'lucide-react'
import { getModels, getLanguages } from '../services/api'
import './ConfigStep.css'

const ConfigStep = ({ config, onConfigChange, onNext, onBack, loading }) => {
  const [models, setModels] = useState([])
  const [languages, setLanguages] = useState([])
  const [loadingData, setLoadingData] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      try {
        const [modelsData, languagesData] = await Promise.all([
          getModels(),
          getLanguages(),
        ])
        setModels(modelsData.models || [])
        setLanguages(languagesData.languages || [])
      } catch (error) {
        console.error('Erro ao carregar dados:', error)
      } finally {
        setLoadingData(false)
      }
    }
    loadData()
  }, [])

  const handleChange = (field, value) => {
    // Para campos numéricos, aplicar limites em tempo real
    if (field === 'batchSize' || field === 'parallel') {
      const numValue = parseInt(value)
      if (!isNaN(numValue)) {
        if (field === 'batchSize') {
          value = Math.min(Math.max(1, numValue), 250)
        } else if (field === 'parallel') {
          value = Math.min(Math.max(1, numValue), 10)
        }
      }
    }
    
    onConfigChange({
      ...config,
      [field]: value,
    })
  }

  return (
    <div className="config-step">
      <div className="config-header">
        <Settings size={48} className="config-icon" />
        <h2>Configuração da Tradução</h2>
        <p>Configure o método e parâmetros de tradução</p>
      </div>

      {loadingData ? (
        <div className="loading-data">
          <Loader2 size={32} className="spinner" />
          <p>Carregando opções...</p>
        </div>
      ) : (
        <div className="config-form">
          <div className="form-group">
            <label>Método de Tradução</label>
            <div className="radio-group">
              <label className="radio-option">
                <input
                  type="radio"
                  name="method"
                  value="openai"
                  checked={config.method === 'openai'}
                  onChange={(e) => handleChange('method', e.target.value)}
                />
                <span>🤖 OpenAI (IA)</span>
              </label>
              <label className="radio-option">
                <input
                  type="radio"
                  name="method"
                  value="google"
                  checked={config.method === 'google'}
                  onChange={(e) => handleChange('method', e.target.value)}
                />
                <span>🌐 Google Translate</span>
              </label>
            </div>
          </div>

          {config.method === 'openai' && (
            <div className="form-group">
              <label>Modelo OpenAI</label>
              <select
                value={config.model}
                onChange={(e) => handleChange('model', e.target.value)}
                className="form-select"
              >
                {models.map((model) => (
                  <option key={model.id} value={model.id}>
                    {model.name} - ${model.pricing.input_per_1m}/1M input, ${model.pricing.output_per_1m}/1M output
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="form-group">
            <label>
              Idioma de Destino
              <span className="hint">(tradução a partir do inglês)</span>
            </label>
            <select
              value={config.targetLanguage}
              onChange={(e) => handleChange('targetLanguage', e.target.value)}
              className="form-select"
            >
              {languages.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>
              Tamanho do Batch
              <span className="hint">(máximo: 250, recomendado: 100-200)</span>
            </label>
            <input
              type="number"
              min="1"
              max="250"
              value={config.batchSize}
              onChange={(e) => handleChange('batchSize', e.target.value)}
              onBlur={(e) => {
                const value = parseInt(e.target.value) || 1
                const clamped = Math.min(Math.max(1, value), 250)
                if (value !== clamped) {
                  handleChange('batchSize', clamped)
                }
              }}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>
              Batches Paralelos
              <span className="hint">(máximo: 10, recomendado: 3-5)</span>
            </label>
            <input
              type="number"
              min="1"
              max="10"
              value={config.parallel}
              onChange={(e) => handleChange('parallel', e.target.value)}
              onBlur={(e) => {
                const value = parseInt(e.target.value) || 1
                const clamped = Math.min(Math.max(1, value), 10)
                if (value !== clamped) {
                  handleChange('parallel', clamped)
                }
              }}
              className="form-input"
            />
          </div>
        </div>
      )}

      <div className="btn-group">
        <button className="btn btn-secondary" onClick={onBack} disabled={loading}>
          Voltar
        </button>
        <button
          className="btn btn-primary"
          onClick={onNext}
          disabled={loading || loadingData}
        >
          {loading ? (
            <>
              <Loader2 size={20} className="spinner" />
              Estimando...
            </>
          ) : (
            'Estimar Custo e Tempo'
          )}
        </button>
      </div>
    </div>
  )
}

export default ConfigStep

