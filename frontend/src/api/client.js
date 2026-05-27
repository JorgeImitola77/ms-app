// Cliente HTTP centralizado para los microservicios.
// Agrega Authorization: Bearer <token>, normaliza el manejo de errores y
// emite eventos globales (`auth:expired`) cuando el JWT del usuario expira
// para que la capa de UI pueda forzar un re-login.

// Mensajes amigables compartidos por todos los módulos del frontend.
export const ERROR_MESSAGES = {
  CONSULTA_UNAVAILABLE: 'El servicio de consulta no está disponible temporalmente.',
  SERVICE_UNAVAILABLE: 'El servicio no está disponible temporalmente. Intenta de nuevo en unos minutos.',
  DB_UNAVAILABLE: 'La base de datos no está disponible en este momento. Intenta de nuevo en unos minutos.',
  AUTH_EXPIRED: 'Tu sesión expiró. Por favor inicia sesión nuevamente.',
  INTERNAL: 'Ocurrió un error interno en el servidor. Por favor intenta de nuevo.',
}

// El microservicio Consultar corre en 8003. Cuando esa URL específica
// devuelve 503/red caída, el mensaje que pide la spec es distinto al
// mensaje genérico de "servicio no disponible".
const CONSULTAR_HOST = 'localhost:8003'

function isConsultarUrl(url) {
  return typeof url === 'string' && url.includes(CONSULTAR_HOST)
}

function unavailableMessage(url) {
  return isConsultarUrl(url)
    ? ERROR_MESSAGES.CONSULTA_UNAVAILABLE
    : ERROR_MESSAGES.SERVICE_UNAVAILABLE
}

function formatPydanticErrors(detail) {
  // FastAPI/Pydantic devuelven `detail` como array de objetos {loc, msg, type}
  // cuando la validación falla con 422. Lo convertimos en un texto legible.
  return detail
    .map((d) => {
      if (!d || typeof d !== 'object') return JSON.stringify(d)
      const campo = Array.isArray(d.loc) ? d.loc.filter((p) => p !== 'body').join('.') : ''
      const mensaje = d.msg || 'Valor inválido'
      return campo ? `${campo}: ${mensaje}` : mensaje
    })
    .join(' · ')
}

export async function apiFetch(url, getToken, options = {}) {
  let token
  try {
    token = await getToken()
  } catch (err) {
    // Auth0 SDK lanza errores cuando la sesión silenciosa no se puede
    // renovar (token expirado, refresh fallido, etc.). Forzamos re-login.
    window.dispatchEvent(new CustomEvent('auth:expired'))
    const error = new Error(ERROR_MESSAGES.AUTH_EXPIRED)
    error.status = 401
    error.cause = err
    throw error
  }

  const headers = {
    Authorization: `Bearer ${token}`,
    ...(options.headers || {}),
  }

  let res
  try {
    res = await fetch(url, { ...options, headers })
  } catch (networkErr) {
    // El contenedor está apagado o no hay red: lo tratamos como 503
    // con el mensaje específico al servicio impactado.
    const error = new Error(unavailableMessage(url))
    error.status = 503
    error.cause = networkErr
    throw error
  }

  // 204 No Content (típico en DELETE) — devolvemos null sin parsear.
  if (res.status === 204) return null

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Error desconocido' }))

    // 401 → JWT expirado o inválido. Disparamos el evento global y
    // dejamos que la UI redirija al login.
    if (res.status === 401) {
      window.dispatchEvent(new CustomEvent('auth:expired'))
      const error = new Error(ERROR_MESSAGES.AUTH_EXPIRED)
      error.status = 401
      throw error
    }

    // 503 → servicio (o BD) caído. Preferimos el `detail` del backend
    // pero si llega vacío usamos el mensaje específico al servicio.
    if (res.status === 503) {
      const msg =
        typeof err?.detail === 'string' && err.detail.trim()
          ? err.detail
          : unavailableMessage(url)
      const error = new Error(msg)
      error.status = 503
      throw error
    }

    const msg =
      typeof err?.detail === 'string'
        ? err.detail
        : Array.isArray(err?.detail)
        ? formatPydanticErrors(err.detail)
        : `Error ${res.status}`
    const error = new Error(msg)
    error.status = res.status
    throw error
  }

  const text = await res.text()
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch {
    return text
  }
}
