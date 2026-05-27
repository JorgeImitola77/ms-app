// Cliente para el webhook RAG expuesto por n8n.
// El workflow espera { pregunta, usuario_id } en el body y responde { pregunta, respuesta }.
// El JWT se envía en Authorization para que quede asociado al request en los logs de n8n.
const RAG_URL = import.meta.env.VITE_N8N_RAG_URL || 'http://localhost:5678/webhook/rag-consulta'
const TIMEOUT_MS = 30000

export async function consultaRAG({ pregunta, usuarioId }, getToken) {
  const token = await getToken()

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
      body: JSON.stringify({ pregunta, usuario_id: usuarioId ?? null }),
      signal: controller.signal,
    })
  } catch (err) {
    clearTimeout(timer)
    if (err.name === 'AbortError') {
      const e = new Error('La consulta tardó demasiado. Intenta de nuevo.')
      e.code = 'TIMEOUT'
      throw e
    }
    const e = new Error('No se pudo conectar con el motor RAG.')
    e.code = 'NETWORK'
    throw e
  }
  clearTimeout(timer)

  if (!res.ok) {
    const e = new Error(
      res.status >= 500
        ? 'El motor RAG falló al procesar la pregunta.'
        : `Error ${res.status} al consultar el motor RAG.`,
    )
    e.status = res.status
    throw e
  }

  const text = await res.text()
  if (!text) {
    const e = new Error('El motor RAG devolvió una respuesta vacía.')
    e.code = 'EMPTY'
    throw e
  }

  try {
    return JSON.parse(text)
  } catch {
    return { pregunta, respuesta: text }
  }
}
