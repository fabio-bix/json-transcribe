import { useState, useRef, useEffect, useMemo } from 'react'
import { ArrowLeft, FileJson, Download, Filter, List, Loader2 } from 'lucide-react'
import { compareJSONs, formatJSONForDisplay } from '../utils/jsonCompare'
import './CompareView.css'

const CompareView = ({ 
  file1Data, 
  file2Data, 
  file1Name, 
  file2Name, 
  currentIndex = 0, 
  totalFiles = 1, 
  fileNames = [], 
  loadingFile = false,
  onSelectFile = () => {}, 
  onBack 
}) => {
  const [syncScroll, setSyncScroll] = useState(true)
  const [filter, setFilter] = useState('all') // 'all', 'added', 'removed', 'modified', 'unchanged'
  const leftPanelRef = useRef(null)
  const rightPanelRef = useRef(null)
  const [differences, setDifferences] = useState(null)
  const [leftLines, setLeftLines] = useState([])
  const [rightLines, setRightLines] = useState([])

  useEffect(() => {
    if (file1Data && file2Data) {
      const diff = compareJSONs(file1Data, file2Data)
      setDifferences(diff)
      setLeftLines(formatJSONForDisplay(file1Data, diff, 'left'))
      setRightLines(formatJSONForDisplay(file2Data, diff, 'right'))
    }
  }, [file1Data, file2Data])

  const handleLeftScroll = (e) => {
    if (syncScroll && rightPanelRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = e.target
      const scrollRatio = scrollTop / (scrollHeight - clientHeight)
      rightPanelRef.current.scrollTop = scrollRatio * (rightPanelRef.current.scrollHeight - rightPanelRef.current.clientHeight)
    }
  }

  const handleRightScroll = (e) => {
    if (syncScroll && leftPanelRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = e.target
      const scrollRatio = scrollTop / (scrollHeight - clientHeight)
      leftPanelRef.current.scrollTop = scrollRatio * (leftPanelRef.current.scrollHeight - leftPanelRef.current.clientHeight)
    }
  }

  const getLineIcon = (status) => {
    switch (status) {
      case 'added':
        return '+'
      case 'removed':
        return '-'
      case 'modified':
        return '~'
      case 'keyChanged':
        return '↔'
      case 'emptyValue':
        return '∅'
      default:
        return ' '
    }
  }

  const stats = differences ? {
    added: differences.added.length,
    removed: differences.removed.length,
    modified: differences.modified.length,
    keyChanged: differences.keyChanged.length,
    emptyValue: differences.emptyValue.length,
    unchanged: differences.unchanged.length,
    total: differences.added.length + differences.removed.length + differences.modified.length + 
           differences.keyChanged.length + differences.emptyValue.length + differences.unchanged.length
  } : null

  // Filtrar linhas baseado no filtro selecionado
  const filteredLeftLines = useMemo(() => {
    if (filter === 'all') return leftLines
    return leftLines.filter(line => line.status === filter)
  }, [leftLines, filter])

  const filteredRightLines = useMemo(() => {
    if (filter === 'all') return rightLines
    return rightLines.filter(line => line.status === filter)
  }, [rightLines, filter])

  // Gerar relatório
  const generateReport = () => {
    if (!differences) return

    const report = {
      metadata: {
        generatedAt: new Date().toISOString(),
        file1: file1Name,
        file2: file2Name,
        totalEntries: stats.total
      },
      summary: {
        added: stats.added,
        removed: stats.removed,
        modified: stats.modified,
        keyChanged: stats.keyChanged,
        emptyValue: stats.emptyValue,
        unchanged: stats.unchanged
      },
      differences: {
        added: differences.added.map(d => ({
          path: d.path,
          value: d.value,
          type: d.type,
          isEmpty: d.isEmpty
        })),
        removed: differences.removed.map(d => ({
          path: d.path,
          value: d.value,
          type: d.type,
          isEmpty: d.isEmpty
        })),
        modified: differences.modified.map(d => ({
          path: d.path,
          oldValue: d.oldValue,
          newValue: d.newValue,
          oldType: d.oldType,
          newType: d.newType
        })),
        keyChanged: differences.keyChanged.map(d => ({
          oldPath: d.oldPath,
          newPath: d.path,
          oldKey: d.oldKey,
          newKey: d.newKey,
          oldValue: d.oldValue,
          newValue: d.newValue,
          type: d.type
        })),
        emptyValue: differences.emptyValue.map(d => ({
          path: d.path,
          oldValue: d.oldValue,
          newValue: d.newValue,
          oldType: d.oldType,
          newType: d.newType,
          isEmptyInFile1: d.isEmptyInFile1,
          isEmptyInFile2: d.isEmptyInFile2
        })),
        unchanged: differences.unchanged.map(d => ({
          path: d.path,
          value: d.value
        }))
      }
    }

    return report
  }

  const handleDownloadReport = () => {
    const report = generateReport()
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5)
    a.download = `comparison-report_${timestamp}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const hasMultipleFiles = totalFiles > 1

  return (
    <div className="compare-view">
      <div className="compare-header-bar">
        <button className="btn btn-secondary" onClick={onBack}>
          <ArrowLeft size={20} />
          Voltar
        </button>
        
        <div className="compare-header-info">
          <div className="file-name-badge">
            <FileJson size={16} />
            <span>{file1Name}</span>
          </div>
          <span className="vs-text">VS</span>
          <div className="file-name-badge">
            <FileJson size={16} />
            <span>{file2Name}</span>
          </div>
        </div>

        <div className="compare-controls">
          <label className="sync-toggle">
            <input
              type="checkbox"
              checked={syncScroll}
              onChange={(e) => setSyncScroll(e.target.checked)}
            />
            <span>Sincronizar rolagem</span>
          </label>
          <button className="btn btn-primary" onClick={handleDownloadReport}>
            <Download size={18} />
            Salvar Relatório
          </button>
        </div>
      </div>

      {hasMultipleFiles && (
        <div className="file-navigation">
          <div className="file-navigation-info">
            <List size={18} />
            <span>Arquivo {currentIndex + 1} de {totalFiles}</span>
          </div>
          
          <div className="file-navigation-controls">
            <div className="file-selector">
              <select
                value={currentIndex}
                onChange={(e) => onSelectFile(parseInt(e.target.value))}
                className="file-select"
                disabled={loadingFile}
              >
                {fileNames.map((name, index) => (
                  <option key={index} value={index}>
                    {index + 1}. {name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}

      {loadingFile && (
        <div className="file-loading-indicator">
          <Loader2 size={20} className="spinner" />
          <span>Carregando arquivo...</span>
        </div>
      )}

      {stats && (
        <>
          <div className="compare-stats">
            <div 
              className={`stat-item stat-added ${filter === 'added' ? 'active' : ''}`}
              onClick={() => setFilter(filter === 'added' ? 'all' : 'added')}
              style={{ cursor: 'pointer' }}
            >
              <span className="stat-label">Adicionadas:</span>
              <span className="stat-value">{stats.added}</span>
            </div>
            <div 
              className={`stat-item stat-removed ${filter === 'removed' ? 'active' : ''}`}
              onClick={() => setFilter(filter === 'removed' ? 'all' : 'removed')}
              style={{ cursor: 'pointer' }}
            >
              <span className="stat-label">Removidas:</span>
              <span className="stat-value">{stats.removed}</span>
            </div>
            <div 
              className={`stat-item stat-key-changed ${filter === 'keyChanged' ? 'active' : ''}`}
              onClick={() => setFilter(filter === 'keyChanged' ? 'all' : 'keyChanged')}
              style={{ cursor: 'pointer' }}
            >
              <span className="stat-label">Chaves Alteradas:</span>
              <span className="stat-value">{stats.keyChanged}</span>
            </div>
            <div 
              className={`stat-item stat-empty-value ${filter === 'emptyValue' ? 'active' : ''}`}
              onClick={() => setFilter(filter === 'emptyValue' ? 'all' : 'emptyValue')}
              style={{ cursor: 'pointer' }}
            >
              <span className="stat-label">Valores Vazios:</span>
              <span className="stat-value">{stats.emptyValue}</span>
            </div>
            <div 
              className={`stat-item stat-modified ${filter === 'modified' ? 'active' : ''}`}
              onClick={() => setFilter(filter === 'modified' ? 'all' : 'modified')}
              style={{ cursor: 'pointer' }}
            >
              <span className="stat-label">Valores Modificados:</span>
              <span className="stat-value">{stats.modified}</span>
            </div>
            <div 
              className={`stat-item stat-unchanged ${filter === 'unchanged' ? 'active' : ''}`}
              onClick={() => setFilter(filter === 'unchanged' ? 'all' : 'unchanged')}
              style={{ cursor: 'pointer' }}
            >
              <span className="stat-label">Inalteradas:</span>
              <span className="stat-value">{stats.unchanged}</span>
            </div>
            <div 
              className={`stat-item ${filter === 'all' ? 'active' : ''}`}
              onClick={() => setFilter('all')}
              style={{ cursor: 'pointer' }}
            >
              <span className="stat-label">Total:</span>
              <span className="stat-value">{stats.total}</span>
            </div>
          </div>
          {filter !== 'all' && (
            <div className="filter-indicator">
              <Filter size={16} />
              <span>Filtrando: {
                filter === 'added' ? 'Adicionadas' : 
                filter === 'removed' ? 'Removidas' : 
                filter === 'modified' ? 'Valores Modificados' : 
                filter === 'keyChanged' ? 'Chaves Alteradas' :
                filter === 'emptyValue' ? 'Valores Vazios' :
                'Inalteradas'
              }</span>
              <button className="filter-clear" onClick={() => setFilter('all')}>
                Limpar filtro
              </button>
            </div>
          )}
        </>
      )}

      <div className="compare-panels">
        <div className="compare-panel">
          <div className="compare-panel-header">
            <h3>{file1Name}</h3>
          </div>
          <div
            className="compare-content"
            ref={leftPanelRef}
            onScroll={handleLeftScroll}
          >
            <div className="compare-lines">
              {filteredLeftLines.length === 0 ? (
                <div className="no-results">
                  <p>Nenhum resultado encontrado para o filtro selecionado.</p>
                </div>
              ) : (
                filteredLeftLines.map((line, index) => (
                  <div
                    key={`left-${line.path}-${index}`}
                    className={`compare-line line-${line.status}`}
                  >
                    <span className="line-number">{index + 1}</span>
                    <span className="line-icon">{getLineIcon(line.status)}</span>
                    <span className="line-content">{line.display}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="compare-divider"></div>

        <div className="compare-panel">
          <div className="compare-panel-header">
            <h3>{file2Name}</h3>
          </div>
          <div
            className="compare-content"
            ref={rightPanelRef}
            onScroll={handleRightScroll}
          >
            <div className="compare-lines">
              {filteredRightLines.length === 0 ? (
                <div className="no-results">
                  <p>Nenhum resultado encontrado para o filtro selecionado.</p>
                </div>
              ) : (
                filteredRightLines.map((line, index) => (
                  <div
                    key={`right-${line.path}-${index}`}
                    className={`compare-line line-${line.status}`}
                  >
                    <span className="line-number">{index + 1}</span>
                    <span className="line-icon">{getLineIcon(line.status)}</span>
                    <span className="line-content">{line.display}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CompareView

