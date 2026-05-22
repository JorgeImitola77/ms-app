import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react'

const ToastContext = createContext(null)

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) {
    throw new Error('useToast debe usarse dentro de <ToastProvider>')
  }
  return ctx
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])
  const idRef = useRef(0)

  const dismiss = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const show = useCallback(
    (message, variant = 'success') => {
      const id = ++idRef.current
      setToasts((prev) => [...prev, { id, message, variant }])
      setTimeout(() => dismiss(id), 4000)
    },
    [dismiss],
  )

  const api = {
    show,
    success: (msg) => show(msg, 'success'),
    error: (msg) => show(msg, 'error'),
    dismiss,
  }

  return (
    <ToastContext.Provider value={api}>
      {children}
      <div className="fixed bottom-4 right-4 z-[60] flex flex-col gap-2 pointer-events-none">
        {toasts.map((t) => (
          <ToastItem key={t.id} toast={t} onClose={() => dismiss(t.id)} />
        ))}
      </div>
    </ToastContext.Provider>
  )
}

function ToastItem({ toast, onClose }) {
  const [visible, setVisible] = useState(false)
  useEffect(() => {
    const tid = requestAnimationFrame(() => setVisible(true))
    return () => cancelAnimationFrame(tid)
  }, [])

  const isError = toast.variant === 'error'
  const palette = isError
    ? 'bg-red-50 border-red-200 text-red-800'
    : 'bg-emerald-50 border-emerald-200 text-emerald-800'
  const dot = isError ? 'bg-red-500' : 'bg-emerald-500'

  return (
    <div
      className={`pointer-events-auto min-w-[260px] max-w-sm rounded-xl border shadow-lg px-4 py-3 flex items-start gap-3 transition-all duration-200 ${palette} ${
        visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
      }`}
      role="status"
    >
      <span className={`mt-1.5 w-2 h-2 rounded-full flex-shrink-0 ${dot}`} />
      <p className="flex-1 text-sm font-medium leading-snug">{toast.message}</p>
      <button
        onClick={onClose}
        className="text-surface-400 hover:text-surface-700 transition-colors"
        aria-label="Cerrar notificación"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  )
}

export default ToastProvider
