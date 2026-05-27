// Cliente para el webhook RAG expuesto por n8n.
// El workflow espera { pregunta, usuario_id } en el body y responde { pregunta, respuesta }.
// El JWT se envía en Authorization para que quede asociado al request en los logs de n8n.
const RAG_URL = import.meta.env.VITE_N8N_RAG_URL || 'http://localhost:5678/webhook/rag-consulta'
const TIMEOUT_MS = 30000

// Mensajes amigables que la UI puede mostrar tal cual al usuario.
export const RAG_ERRORS = {
  TIMEOUT: 'El asistente está tardando más de lo normal, intenta de nuevo.',
  NETWORK: 'El asistente no está disponible temporalmente. Intenta de nuevo en unos minutos.',
  SERVER: 'El asistente falló al procesar la pregunta. Intenta de nuevo.',
  EMPTY: 'El asistente no devolvió una respuesta. Intenta reformular la pregunta.',
  AUTH: 'Tu sesión expiró. Por favor inicia sesión nuevamente.',
}

export async function consultaRAG({ pregunta, usuarioId, email }, getToken) {
  let token
  try {
    token = await getToken()
  } catch (err) {
    window.dispatchEvent(new CustomEvent('auth:expired'))
    const e = new Error(RAG_ERRORS.AUTH)
    e.code = 'AUTH'
    e.status = 401
    throw e
  }

  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS)

  let res
  try {
    res = await fetch(RAG_URL, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        pregunta,
        // El campo `usuario_id` se mantiene por retro-compatibilidad con el workflow
        // de n8n; transporta el `sub` de Auth0 (auth0_id), no un UUID.
        usuario_id: usuarioId ?? null,
        auth0_id: usuarioId ?? null,
        email: email ?? null,
      }),
      signal: controller.signal,
    })
  } catch (err) {
    clearTimeout(timer)
    if (err.name === 'AbortError') {
      const e = new Error(RAG_ERRORS.TIMEOUT)
      e.code = 'TIMEOUT'
      throw e
    }
    const e = new Error(RAG_ERRORS.NETWORK)
    e.code = 'NETWORK'
    throw e
  }
  clearTimeout(timer)

  if (res.status === 401) {
    window.dispatchEvent(new CustomEvent('auth:expired'))
    const e = new Error(RAG_ERRORS.AUTH)
    e.code = 'AUTH'
    e.status = 401
    throw e
  }

  if (!res.ok) {
    // Si el motor responde 504 (gateway timeout) tratamos también como timeout
    // amigable para que el usuario reintente.
    if (res.status === 504 || res.status === 408) {
      const e = new Error(RAG_ERRORS.TIMEOUT)
      e.code = 'TIMEOUT'
      e.status = res.status
      throw e
    }
    const e = new Error(
      res.status >= 500 ? RAG_ERRORS.SERVER : `Error ${res.status} al consultar el asistente.`,
    )
    e.status = res.status
    throw e
  }

  const text = await res.text()
  if (!text) {
    const e = new Error(RAG_ERRORS.EMPTY)
    e.code = 'EMPTY'
    throw e
  }

  try {
    return JSON.parse(text)
  } catch {
    return { pregunta, respuesta: text }
  }
}
