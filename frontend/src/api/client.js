// Cliente HTTP centralizado para los microservicios.
// Agrega Authorization: Bearer <token> y normaliza el manejo de errores.
export async function apiFetch(url, getToken, options = {}) {
  const token = await getToken()

  const headers = {
    Authorization: `Bearer ${token}`,
    ...(options.headers || {}),
  }

  let res
  try {
    res = await fetch(url, { ...options, headers })
  } catch (networkErr) {
    // El contenedor está apagado o no hay red: lo tratamos como 503
    // para que la UI muestre el mismo mensaje amigable.
    const error = new Error('El servicio no está disponible en este momento.')
    error.status = 503
    error.cause = networkErr
    throw error
  }

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
