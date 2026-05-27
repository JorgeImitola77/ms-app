# Manejo de errores y casos límite — ExplorApp (sección 7)

**Fecha:** 2026-05-27
**Branch:** `feature/86e19t0h2`
**Card ClickUp:** [86e19t0h2](https://app.clickup.com/t/86e19t0h2)
**Alcance:** Microservicios FastAPI (`ms-crear`, `ms-modificar`, `ms-consultar`,
`ms-borrar`, `ms-log`), cliente HTTP del frontend (`frontend/src/api/`),
flujo RAG (n8n).

> Objetivo: completar el manejo de errores y casos límite documentados en la
> sección 7 del documento de diseño. Todos los mensajes mostrados al usuario
> están en español, son claros y útiles, y no filtran información interna de
> la infraestructura.

---

## 1. Resumen ejecutivo

| # | Escenario                              | Status backend | Mensaje al usuario |
|---|----------------------------------------|----------------|--------------------|
| 1 | Datos inválidos (Pydantic)             | `422`          | Lista de errores por campo, mostrados en Tailwind. |
| 2 | Servicio Consulta apagado              | `503` (frontend) | "El servicio de consulta no está disponible temporalmente." |
| 3 | Timeout del LLM/n8n                    | `AbortError` / `504` / `408` | "El asistente está tardando más de lo normal, intenta de nuevo." |
| 4 | Foto > 2 MB                            | `422` (servidor) + bloqueo en cliente | "La foto no debe superar los 2 MB." |
| 5 | JWT expirado                           | `401`          | "Tu sesión expiró. Por favor inicia sesión nuevamente." + re-login automático. |
| 6 | DB caída                               | `503`          | "La base de datos no está disponible en este momento. Por favor intenta de nuevo en unos minutos." |
| 6b| Error interno no clasificado           | `500`          | "Ocurrió un error interno en el servidor. Por favor intenta de nuevo en unos minutos." |
| 7 | 409 conflicto en Crear                 | `409`          | "Ya existe una persona con ese documento." |

Todos los handlers de cada microservicio reutilizan el módulo compartido
`microservicios/shared/errors.py`, que centraliza:

- `is_db_connection_error(exc)` → clasifica fallos de conexión a PostgreSQL.
- `raise_for_unexpected(exc)` → traduce excepciones inesperadas a 503/500
  con mensaje amigable, sin filtrar `str(exc)` al cliente.

---

## 2. Datos inválidos → 422 con detalle Pydantic

**Frontend:** `frontend/src/pages/CrearPersona.jsx` y `ModificarPersona.jsx`
validan en cliente con Tailwind (mensajes rojos bajo cada input).

**Backend `ms-modificar`:** `PersonaUpdate` (Pydantic) se inyecta como body
en el endpoint, por lo que FastAPI ya devuelve 422 automáticamente.

**Backend `ms-crear`:** el endpoint usa `Form(...)` (multipart) para poder
recibir la foto, por lo que la validación Pydantic no es automática. Se
añadió una validación manual usando `PersonaCreate` de `shared.models`:

```python
try:
    PersonaCreate(
        tipo_documento=tipo_documento,
        nro_documento=nro_documento,
        ...
    )
except ValidationError as exc:
    raise HTTPException(status_code=422, detail=exc.errors())
```

El cliente HTTP formatea la lista de errores Pydantic en un toast legible
(`frontend/src/api/client.js → formatPydanticErrors`).

---

## 3. Servicio Consulta apagado → 503 amigable

`apiFetch` (frontend/src/api/client.js) detecta:

1. **Fallo de red** (microservicio caído, sin conexión): el `fetch` lanza
   `TypeError: Failed to fetch` → se convierte a `Error` con `status=503` y
   mensaje específico al host de la URL.
2. **Respuesta 503 del backend** (BD caída u otro servicio interno): toma el
   `detail` del backend, o usa el mensaje específico si viene vacío.

Para URLs del servicio Consulta (`localhost:8003`), el mensaje es:
"El servicio de consulta no está disponible temporalmente.". Para otros
servicios usa el mensaje genérico.

---

## 4. Timeout del LLM/n8n

`frontend/src/api/rag.js` configura un `AbortController` con `TIMEOUT_MS = 30000`.
Si el webhook RAG tarda más de 30s o si el motor devuelve 504/408:

```js
RAG_ERRORS.TIMEOUT =
  'El asistente está tardando más de lo normal, intenta de nuevo.'
```

El `ChatRAG` ya muestra el `err.message` en el toast y en el burbuja
de error → ningún cambio adicional necesario en el componente.

---

## 5. Foto > 2 MB (cliente y servidor)

**Cliente** (`CrearPersona.jsx`): se valida el `file.size > 2 * 1024 * 1024`
antes de subir y se muestra un error rojo de Tailwind.

**Servidor** (`ms-crear/main.py`):

```python
MAX_FOTO_BYTES = 2 * 1024 * 1024
if len(contenido) > MAX_FOTO_BYTES:
    raise HTTPException(
        status_code=422,
        detail="La foto no debe superar los 2 MB.",
    )
```

Además se valida el `content_type` para rechazar archivos que no sean
imágenes (`!content_type.startswith("image/")` → 422).

---

## 6. JWT expirado → re-login automático

**Backend:** `shared/auth.py` ya maneja `ExpiredSignatureError` → `401`
con `WWW-Authenticate: Bearer`.

**Frontend:** `apiFetch` detecta `401` y dispara un evento global:

```js
window.dispatchEvent(new CustomEvent('auth:expired'))
```

`App.jsx` escucha ese evento con `useAuthExpiredRedirect`, hace `logout`
local (sin redirigir a la URL de logout de Auth0) y llama
`loginWithRedirect`. El usuario vuelve a `/app` tras autenticarse.

El mismo evento se dispara cuando `getAccessTokenSilently()` falla (refresh
token caducado, sesión silenciosa rota, etc.), por lo que no se requiere
botón "Volver a iniciar sesión" en cada página.

---

## 7. DB caída → 503 amigable

Antes, todos los `except Exception` devolvían `500` con `detail=str(e)`,
lo que filtraba el mensaje de asyncpg (incluyendo a veces la URL de
conexión). Ahora cada microservicio usa:

```python
from shared.errors import raise_for_unexpected, is_db_connection_error, DB_UNAVAILABLE_MSG

try:
    conn = await get_db_connection()
except Exception as exc:
    if is_db_connection_error(exc):
        raise HTTPException(503, detail=DB_UNAVAILABLE_MSG)
    raise_for_unexpected(exc)
```

`is_db_connection_error` reconoce `OSError`, `ConnectionError`,
`TimeoutError` y las excepciones de `asyncpg.exceptions` cuyo nombre está
en la whitelist (`CannotConnectNowError`, `ConnectionDoesNotExistError`,
`ConnectionFailureError`, `PostgresConnectionError`, `InterfaceError`).

Cualquier otra excepción cae en el `500` genérico con mensaje:
"Ocurrió un error interno en el servidor. Por favor intenta de nuevo en unos minutos."

---

## 8. 409 conflicto en Crear

`ms-crear` captura `asyncpg.exceptions.UniqueViolationError` y devuelve:

```python
raise HTTPException(
    status_code=409,
    detail="Ya existe una persona con ese documento.",
)
```

El frontend lo muestra tal cual mediante el toast (no hay tratamiento
especial; el mensaje del backend es el que se exhibe).

---

## 9. Pruebas

| Escenario                       | Pytest                                                  |
|---------------------------------|---------------------------------------------------------|
| 422 datos inválidos (Pydantic)  | `test_crear_persona_pydantic_validation_422`            |
| 422 campo faltante              | `test_crear_persona_422_falta_campo_obligatorio`        |
| 409 documento duplicado         | `test_crear_persona_documento_duplicado_devuelve_409`   |
| 500 genérico (no filtra exc)    | `test_*_error_db_devuelve_500` (×5)                     |
| 503 DB caída                    | `test_*_db_caida_devuelve_503` (×5)                     |
| Foto > 2 MB                     | `test_crear_persona_rechaza_foto_mayor_a_2mb`           |

Total: **126 tests pasando** (`test.bat` opción 1).

Las pruebas manuales del frontend (re-login con JWT expirado, banner de
servicio caído, timeout del chat RAG) se ejecutan siguiendo los pasos
descritos en cada sección anterior.
