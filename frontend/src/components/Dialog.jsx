import { X, AlertCircle, CheckCircle2, AlertTriangle } from 'lucide-react'
import './Dialog.css'

const Dialog = ({ isOpen, onClose, title, message, type = 'info', onConfirm, confirmText = 'OK', cancelText = 'Cancelar', showCancel = false }) => {
  if (!isOpen) return null

  const handleConfirm = () => {
    if (onConfirm) {
      onConfirm()
    }
    onClose()
  }

  const handleCancel = () => {
    onClose()
  }

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle2 size={24} className="dialog-icon success" />
      case 'error':
        return <AlertCircle size={24} className="dialog-icon error" />
      case 'warning':
        return <AlertTriangle size={24} className="dialog-icon warning" />
      default:
        return <AlertCircle size={24} className="dialog-icon info" />
    }
  }

  return (
    <div className="dialog-overlay" onClick={handleCancel}>
      <div className="dialog" onClick={(e) => e.stopPropagation()}>
        <div className="dialog-header">
          <div className="dialog-title-wrapper">
            {getIcon()}
            <h3 className="dialog-title">{title}</h3>
          </div>
          <button className="dialog-close" onClick={handleCancel}>
            <X size={20} />
          </button>
        </div>
        <div className="dialog-content">
          <p>{message}</p>
        </div>
        <div className="dialog-actions">
          {showCancel && (
            <button className="btn btn-secondary" onClick={handleCancel}>
              {cancelText}
            </button>
          )}
          <button className={`btn btn-primary dialog-${type}`} onClick={handleConfirm}>
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  )
}

export default Dialog

