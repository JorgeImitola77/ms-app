import PageHeader from '../components/ui/PageHeader'

export default function ChatRAG() {
  return (
    <div>
      <PageHeader
        title="Consulta en Lenguaje Natural"
        description="Haz preguntas sobre los datos registrados usando lenguaje natural (RAG + n8n)."
      />

      <div className="card max-w-4xl mx-auto p-0 overflow-hidden" style={{ height: 'calc(100vh - 220px)' }}>
        <div className="h-full flex flex-col">
          {/* Info Banner */}
          <div className="px-6 py-3 bg-violet-50 border-b border-violet-100 flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-violet-100 flex items-center justify-center">
              <svg className="w-4 h-4 text-violet-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 0 0-2.455 2.456Z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium text-violet-800">Motor RAG con n8n</p>
              <p className="text-xs text-violet-500">Las preguntas y respuestas quedan registradas en el log de auditoría.</p>
            </div>
          </div>

          {/* Chat Area */}
          <div className="flex-1 flex flex-col items-center justify-center p-8 bg-surface-50/50">
            <div className="text-center max-w-sm">
              <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-violet-100 to-brand-100 flex items-center justify-center mx-auto">
                <svg className="w-10 h-10 text-violet-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 0 1 1.037-.443 48.282 48.282 0 0 0 5.68-.494c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z" />
                </svg>
              </div>
              <h3 className="mt-6 font-display font-semibold text-lg text-surface-800">Chat de n8n</h3>
              <p className="mt-2 text-sm text-surface-600 leading-relaxed">
                Aquí se embebe la interfaz de chat de n8n. Puedes preguntar cosas como:
              </p>
              <div className="mt-4 space-y-2">
                {[
                  '¿Cuál es el empleado más joven?',
                  '¿Cuántas personas hay registradas?',
                  'Lista las personas con cédula',
                ].map((q) => (
                  <div
                    key={q}
                    className="px-4 py-2.5 bg-white rounded-xl border border-surface-200 text-sm text-surface-600 text-left cursor-default hover:border-violet-300 hover:text-violet-700 transition-colors"
                  >
                    "{q}"
                  </div>
                ))}
              </div>

              <div className="mt-8 p-4 rounded-xl bg-surface-100 border border-dashed border-surface-300">
                <p className="text-xs text-surface-500 font-mono">{'<!-- n8n chat iframe goes here -->'}</p>
                <p className="text-xs text-surface-500 mt-1">Puerto: localhost:5678</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
