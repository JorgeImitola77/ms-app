// Cliente HTTP centralizado para los microservicios.
// Agrega Authorization: Bearer <token> y normaliza el manejo de errores.
export async function apiFetch(url, getToken, options = {}) {
  const token = await getToken()

  const headers = {
    Authorization: `Bearer ${token}`,
    ...(options.headers || {}),
  }

  const res = await fetch(url, { ...options, headers })

  // 204 No Content (típico en DELETE) — devolvemos null sin parsear.
  if (res.status === 204) return null

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Error desconocido' }))
    const msg =
      typeof err?.detail === 'string'
        ? err.detail
        : Array.isArray(err?.detail)
        ? err.detail.map((d) => d?.msg || JSON.stringify(d)).join(' · ')
        : `Error ${res.status}`
    const error = new Error(msg)
    error.status = res.status
    throw error
  }

  // Algunas respuestas pueden venir vacías.
  const text = await res.text()
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch {
    return text
  }
}
