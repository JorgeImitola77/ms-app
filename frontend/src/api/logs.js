import { apiFetch } from './client'

const LOGS_URL = 'http://localhost:8005/api/logs'

export function consultarLogs(filtros = {}, getToken) {
  const params = new URLSearchParams()
  if (filtros.tipo) params.append('tipo', filtros.tipo)
  if (filtros.documento) params.append('documento', filtros.documento)
  if (filtros.fecha) params.append('fecha', filtros.fecha)

  const qs = params.toString()
  const url = qs ? `${LOGS_URL}?${qs}` : LOGS_URL

  return apiFetch(url, getToken, { method: 'GET' })
}
