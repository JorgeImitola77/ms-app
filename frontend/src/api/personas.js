import { apiFetch } from './client'

const CREAR_URL = 'http://localhost:8001/api/personas'
const CONSULTAR_URL = 'http://localhost:8003/api/personas'
const MODIFICAR_URL = 'http://localhost:8002/api/personas'
const BORRAR_URL = 'http://localhost:8004/api/personas'

// Crear: multipart/form-data. NO seteamos Content-Type para que el browser
// genere el boundary automáticamente.
export function crearPersona(formData, getToken) {
  return apiFetch(CREAR_URL, getToken, {
    method: 'POST',
    body: formData,
  })
}

export function consultarPersona(documento, getToken) {
  return apiFetch(
    `${CONSULTAR_URL}/${encodeURIComponent(documento)}`,
    getToken,
    { method: 'GET' },
  )
}

export function modificarPersona(documento, datos, getToken) {
  return apiFetch(
    `${MODIFICAR_URL}/${encodeURIComponent(documento)}`,
    getToken,
    {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos),
    },
  )
}

export function borrarPersona(documento, getToken) {
  return apiFetch(
    `${BORRAR_URL}/${encodeURIComponent(documento)}`,
    getToken,
    { method: 'DELETE' },
  )
}
