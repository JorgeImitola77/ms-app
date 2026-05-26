import { useCallback, useEffect, useRef, useState } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import PageHeader from '../components/ui/PageHeader'
import { useToast } from '../components/ui/Toast'
import { consultaRAG } from '../api/rag'

const STORAGE_KEY = 'explorapp.chat-rag.messages'

const SUGGESTIONS = [
  '¿Cuál es el empleado más joven?',
  '¿Cuántas personas hay registradas?',
  'Lista las personas con cédula',
]

function loadInitialMessages() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function timeLabel(ts) {
  try {
    return new Date(ts).toLocaleTimeString('es-CO', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    })
  } catch {
    return ''
  }
}

export default function ChatRAG() {
  const { user, getAccessTokenSilently } = useAuth0()
  const toast = useToast()

  const [messages, setMessages] = useState(loadInitialMessages)
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)

  const scrollRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(messages))
    } catch {
      // sessionStorage lleno o bloqueado: la sesión sigue funcionando en memoria.
    }
  }, [messages])

  useEffect(() => {
    const el = scrollRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [messages, sending])

  const enviar = useCallback(
    async (texto) => {
      const pregunta = (texto ?? input).trim()
      if (!pregunta || sending) return

      setInput('')
      const ts = Date.now()
      setMessages((prev) => [
        ...prev,
        { id: `u-${ts}`, role: 'user', text: pregunta, ts },
      ])
      setSending(true)

      try {
        const data = await consultaRAG(
          { pregunta, usuarioId: user?.sub ?? null },
          getAccessTokenSilently,
        )
        const respuesta =
          (data && typeof data.respuesta === 'string' && data.respuesta.trim()) ||
          'No encontré información para responder esa pregunta.'
        setMessages((prev) => [
          ...prev,
          { id: `a-${Date.now()}`, role: 'assistant', text: respuesta, ts: Date.now() },
        ])
      } catch (err) {
        const msg = err?.message || 'Error al consultar el motor RAG.'
        setMessages((prev) => [
          ...prev,
          {
            id: `e-${Date.now()}`,
            role: 'assistant',
            text: msg,
            ts: Date.now(),
            error: true,
          },
        ])
        toast.error(msg)
      } finally {
        setSending(false)
        inputRef.current?.focus()
      }
    },
    [input, sending, user, getAccessTokenSilently, toast],
  )

  const handleSubmit = (e) => {
    e.preventDefault()
    enviar()
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      enviar()
    }
  }

  const limpiar = () => {
    setMessages([])
    try {
      sessionStorage.removeItem(STORAGE_KEY)
    } catch {
      // ignore
    }
  }

  const isEmpty = messages.length === 0

  return (
    <div>
      <PageHeader
        title="Consulta en Lenguaje Natural"
        description="Haz preguntas sobre los datos registrados usando lenguaje natural (RAG + n8n)."
      />

      <div
        className="card max-w-4xl mx-auto p-0 overflow-hidden"
        style={{ height: 'calc(100vh - 220px)' }}
      >
        <div className="h-full flex flex-col">
          {/* Info Banner */}
          <div className="px-6 py-3 bg-violet-50 border-b border-violet-100 flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-violet-100 flex items-center justify-center">
              <svg
                className="w-4 h-4 text-violet-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 0 0-2.455 2.456Z"
                />
              </svg>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-violet-800">Motor RAG con n8n</p>
              <p className="text-xs text-violet-500">
                Las preguntas y respuestas quedan registradas en el log de auditoría.
              </p>
            </div>
            {!isEmpty && (
              <button
                type="button"
                onClick={limpiar}
                className="text-xs font-medium text-violet-600 hover:text-violet-800 transition-colors"
              >
                Limpiar conversación
              </button>
            )}
          </div>

          {/* Chat Area */}
          <div
            ref={scrollRef}
            className="flex-1 overflow-y-auto px-4 sm:px-6 py-6 bg-surface-50/50"
          >
            {isEmpty ? (
              <div className="h-full flex flex-col items-center justify-center text-center">
                <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-violet-100 to-brand-100 flex items-center justify-center mx-auto">
                  <svg
                    className="w-10 h-10 text-violet-500"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={1}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 0 1 1.037-.443 48.282 48.282 0 0 0 5.68-.494c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z"
                    />
                  </svg>
                </div>
                <h3 className="mt-6 font-display font-semibold text-lg text-surface-800">
                  Empieza una conversación
                </h3>
                <p className="mt-2 text-sm text-surface-600 max-w-sm">
                  Pregunta lo que necesites sobre las personas registradas. Por ejemplo:
                </p>
                <div className="mt-4 space-y-2 w-full max-w-sm">
                  {SUGGESTIONS.map((q) => (
                    <button
                      key={q}
                      type="button"
                      onClick={() => enviar(q)}
                      disabled={sending}
                      className="w-full px-4 py-2.5 bg-white rounded-xl border border-surface-200 text-sm text-surface-600 text-left hover:border-violet-300 hover:text-violet-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      &ldquo;{q}&rdquo;
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-4 max-w-3xl mx-auto">
                {messages.map((m) => (
                  <MessageBubble key={m.id} message={m} />
                ))}
                {sending && <TypingBubble />}
              </div>
            )}
          </div>

          {/* Input */}
          <form
            onSubmit={handleSubmit}
            className="border-t border-surface-100 bg-white px-4 sm:px-6 py-3"
          >
            <div className="flex items-end gap-2 max-w-3xl mx-auto">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Escribe tu pregunta..."
                rows={1}
                disabled={sending}
                className="input-field text-sm resize-none max-h-32"
                style={{ minHeight: '42px' }}
                aria-label="Pregunta para el motor RAG"
              />
              <button
                type="submit"
                disabled={sending || !input.trim()}
                className="btn-primary py-2.5 px-4 text-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {sending ? (
                  <>
                    <span className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
                    <span>Enviando</span>
                  </>
                ) : (
                  <>
                    <span>Enviar</span>
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={2}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5"
                      />
                    </svg>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  const isError = message.error

  const wrapperClass = isUser ? 'justify-end' : 'justify-start'
  const bubbleClass = isUser
    ? 'bg-brand-600 text-white rounded-br-md'
    : isError
    ? 'bg-red-50 text-red-800 border border-red-200 rounded-bl-md'
    : 'bg-white text-surface-800 border border-surface-200 rounded-bl-md'

  return (
    <div className={`flex ${wrapperClass}`}>
      <div className={`max-w-[80%] rounded-2xl px-4 py-2.5 shadow-sm ${bubbleClass}`}>
        <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.text}</p>
        <p
          className={`text-[10px] mt-1 text-right ${
            isUser ? 'text-white/70' : isError ? 'text-red-500' : 'text-surface-400'
          }`}
        >
          {timeLabel(message.ts)}
        </p>
      </div>
    </div>
  )
}

function TypingBubble() {
  return (
    <div className="flex justify-start" aria-live="polite" aria-label="El asistente está escribiendo">
      <div className="bg-white border border-surface-200 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm flex items-center gap-1.5">
        <span className="w-2 h-2 rounded-full bg-violet-400 animate-bounce" style={{ animationDelay: '0ms' }} />
        <span className="w-2 h-2 rounded-full bg-violet-400 animate-bounce" style={{ animationDelay: '150ms' }} />
        <span className="w-2 h-2 rounded-full bg-violet-400 animate-bounce" style={{ animationDelay: '300ms' }} />
        <span className="ml-2 text-xs text-surface-500">escribiendo...</span>
      </div>
    </div>
  )
}
