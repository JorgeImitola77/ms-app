import { useCallback, useEffect, useState } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import PageHeader from '../components/ui/PageHeader'
import { useToast } from '../components/ui/Toast'
import { consultarLogs } from '../api/logs'

const typeColors = {
  CREAR: 'bg-emerald-50 text-emerald-700',
  CONSULTAR: 'bg-blue-50 text-blue-700',
  ACTUALIZAR: 'bg-amber-50 text-amber-700',
  BORRAR: 'bg-red-50 text-red-700',
  CONSULTA_RAG: 'bg-violet-50 text-violet-700',
}

function formatFecha(value) {
  if (!value) return '—'
  // El backend devuelve timestamps sin sufijo de zona (UTC implícito desde PostgreSQL).
  // Añadimos 'Z' para que el parser de Date lo interprete como UTC y luego
  // lo convertimos a America/Bogota (UTC-5).
  const iso = value.includes('T') ? value : value.replace(' ', 'T')
  const d = new Date(iso.endsWith('Z') ? iso : iso + 'Z')
  if (Number.isNaN(d.getTime())) return value
  return d.toLocaleString('es-CO', {
    timeZone: 'America/Bogota',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })
}

export default function Logs() {
  const { getAccessTokenSilently } = useAuth0()
  const toast = useToast()

  const [filtros, setFiltros] = useState({ tipo: '', documento: '', fecha: '' })
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchLogs = useCallback(
    async (params = {}) => {
      setLoading(true)
      setError(null)
      try {
        const data = await consultarLogs(params, getAccessTokenSilently)
        setLogs(Array.isArray(data) ? data : data?.logs ?? [])
      } catch (err) {
        setError(err.message || 'Error al cargar los logs.')
        toast.error(err.message || 'Error al cargar los logs.')
        setLogs([])
      } finally {
        setLoading(false)
      }
    },
    [getAccessTokenSilently, toast],
  )

  useEffect(() => {
    fetchLogs()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleFilter = (e) => {
    e?.preventDefault?.()
    fetchLogs(filtros)
  }

  const setFiltro = (name, value) => {
    setFiltros((prev) => ({ ...prev, [name]: value }))
  }

  return (
    <div>
      <PageHeader
        title="Historial de Transacciones"
        description="Registro completo de todas las operaciones del sistema."
      />

      {/* Filters */}
      <form onSubmit={handleFilter} className="card mb-6">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="sm:w-48">
            <label className="label">Tipo de transacción</label>
            <select
              className="input-field text-sm"
              value={filtros.tipo}
              onChange={(e) => setFiltro('tipo', e.target.value)}
            >
              <option value="">Todos</option>
              <option value="CREAR">Crear</option>
              <option value="CONSULTAR">Consultar</option>
              <option value="ACTUALIZAR">Actualizar</option>
              <option value="BORRAR">Borrar</option>
              <option value="CONSULTA_RAG">Consulta RAG</option>
            </select>
          </div>
          <div className="sm:w-48">
            <label className="label">Documento</label>
            <input
              type="text"
              className="input-field text-sm"
              placeholder="Nro. documento..."
              maxLength={10}
              inputMode="numeric"
              value={filtros.documento}
              onChange={(e) => setFiltro('documento', e.target.value.replace(/\D/g, ''))}
            />
          </div>
          <div className="sm:w-48">
            <label className="label">Fecha</label>
            <input
              type="date"
              className="input-field text-sm"
              value={filtros.fecha}
              onChange={(e) => setFiltro('fecha', e.target.value)}
            />
          </div>
          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading}
              className="btn-primary py-2.5 px-5 text-sm disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? 'Filtrando...' : 'Filtrar'}
            </button>
          </div>
        </div>
      </form>

      {/* Table */}
      <div className="card p-0 overflow-hidden">
        {loading ? (
          <div className="flex flex-col items-center py-16 gap-3">
            <div className="w-8 h-8 rounded-full border-2 border-brand-600 border-t-transparent animate-spin" />
            <p className="text-sm text-surface-500">Cargando logs...</p>
          </div>
        ) : error ? (
          <div className="py-16 text-center">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        ) : logs.length === 0 ? (
          <div className="py-16 text-center">
            <p className="text-sm text-surface-500">No se encontraron registros con los filtros actuales.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-surface-100">
                  {['ID', 'Fecha', 'Tipo', 'Documento', 'Detalle'].map((col) => (
                    <th key={col} className="text-left text-xs font-semibold text-surface-500 uppercase tracking-wider px-6 py-3 font-body whitespace-nowrap">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => {
                  const isRag = log.tipo_transaccion === 'CONSULTA_RAG'
                  return (
                    <tr key={log.id_log} className="border-b border-surface-50 hover:bg-surface-50/50 transition-colors align-top">
                      <td className="px-6 py-3.5 text-sm font-mono text-surface-600">#{log.id_log}</td>
                      <td className="px-6 py-3.5 text-sm text-surface-600 whitespace-nowrap">{formatFecha(log.fecha_transaccion)}</td>
                      <td className="px-6 py-3.5">
                        <span className={`inline-flex px-2.5 py-0.5 rounded-md text-xs font-medium ${typeColors[log.tipo_transaccion] || 'bg-surface-100 text-surface-600'}`}>
                          {log.tipo_transaccion}
                        </span>
                      </td>
                      <td className="px-6 py-3.5 text-sm font-mono text-surface-600">{log.documento_relacionado || '—'}</td>
                      <td className="px-6 py-3.5">
                        {isRag ? (
                          <div className="space-y-1.5 max-w-2xl">
                            {log.pregunta_rag && (
                              <p className="text-sm text-surface-700 whitespace-pre-wrap break-words">
                                <span className="font-semibold text-violet-700">P:</span> {log.pregunta_rag}
                              </p>
                            )}
                            {log.respuesta_rag && (
                              <p className="text-sm text-surface-600 whitespace-pre-wrap break-words">
                                <span className="font-semibold text-violet-700">R:</span> {log.respuesta_rag}
                              </p>
                            )}
                            {log.detalle && (
                              <p className="text-xs text-surface-400 italic break-words">{log.detalle}</p>
                            )}
                          </div>
                        ) : (
                          <p className="text-sm text-surface-600 whitespace-pre-wrap break-words max-w-xl">
                            {log.detalle || '—'}
                          </p>
                        )}
                        {log.email_usuario && (
                          <p className="text-xs text-surface-400 mt-1.5">
                            Por usuario: <span className="font-medium text-surface-500">{log.email_usuario}</span>
                          </p>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}

        {!loading && !error && logs.length > 0 && (
          <div className="px-6 py-3 border-t border-surface-100 bg-surface-50/50 flex items-center justify-between">
            <p className="text-xs text-surface-500">Mostrando {logs.length} registros</p>
          </div>
        )}
      </div>
    </div>
  )
}
