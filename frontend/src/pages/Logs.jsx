import PageHeader from '../components/ui/PageHeader'

const mockLogs = [
  { id_log: 1, fecha_transaccion: '2026-05-09 14:32:10', tipo_transaccion: 'CREAR', documento_relacionado: '1020304050', detalle: 'Creación exitosa de Juan Pérez' },
  { id_log: 2, fecha_transaccion: '2026-05-09 14:35:22', tipo_transaccion: 'CONSULTAR', documento_relacionado: '1020304050', detalle: 'Consulta de datos personales' },
  { id_log: 3, fecha_transaccion: '2026-05-09 15:01:45', tipo_transaccion: 'ACTUALIZAR', documento_relacionado: '1020304050', detalle: 'Modificación de correo y celular' },
  { id_log: 4, fecha_transaccion: '2026-05-09 15:10:00', tipo_transaccion: 'CONSULTA_RAG', documento_relacionado: null, detalle: 'Pregunta: ¿Cuál es el empleado más joven?' },
  { id_log: 5, fecha_transaccion: '2026-05-09 16:22:33', tipo_transaccion: 'BORRAR', documento_relacionado: '9876543210', detalle: 'Eliminación de María López' },
  { id_log: 6, fecha_transaccion: '2026-05-08 09:15:00', tipo_transaccion: 'CREAR', documento_relacionado: '5544332211', detalle: 'Creación exitosa de Pedro Gómez' },
]

const typeColors = {
  CREAR: 'bg-emerald-50 text-emerald-700',
  CONSULTAR: 'bg-blue-50 text-blue-700',
  ACTUALIZAR: 'bg-amber-50 text-amber-700',
  BORRAR: 'bg-red-50 text-red-700',
  CONSULTA_RAG: 'bg-violet-50 text-violet-700',
}

export default function Logs() {
  return (
    <div>
      <PageHeader
        title="Historial de Transacciones"
        description="Registro completo de todas las operaciones del sistema."
      />

      {/* Filters */}
      <div className="card mb-6">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="sm:w-48">
            <label className="label">Tipo de transacción</label>
            <select className="input-field text-sm" defaultValue="">
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
            <input type="text" className="input-field text-sm" placeholder="Nro. documento..." maxLength={10} />
          </div>
          <div className="sm:w-48">
            <label className="label">Fecha</label>
            <input type="date" className="input-field text-sm" />
          </div>
          <div className="flex items-end">
            <button className="btn-primary py-2.5 px-5 text-sm">Filtrar</button>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="card p-0 overflow-hidden">
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
              {mockLogs.map((log) => (
                <tr key={log.id_log} className="border-b border-surface-50 hover:bg-surface-50/50 transition-colors">
                  <td className="px-6 py-3.5 text-sm font-mono text-surface-600">#{log.id_log}</td>
                  <td className="px-6 py-3.5 text-sm text-surface-600 whitespace-nowrap">{log.fecha_transaccion}</td>
                  <td className="px-6 py-3.5">
                    <span className={`inline-flex px-2.5 py-0.5 rounded-md text-xs font-medium ${typeColors[log.tipo_transaccion] || 'bg-surface-100 text-surface-600'}`}>
                      {log.tipo_transaccion}
                    </span>
                  </td>
                  <td className="px-6 py-3.5 text-sm font-mono text-surface-600">{log.documento_relacionado || '—'}</td>
                  <td className="px-6 py-3.5 text-sm text-surface-600 max-w-xs truncate">{log.detalle}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="px-6 py-3 border-t border-surface-100 bg-surface-50/50 flex items-center justify-between">
          <p className="text-xs text-surface-500">Mostrando {mockLogs.length} registros</p>
        </div>
      </div>
    </div>
  )
}
