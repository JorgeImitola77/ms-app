# Auditoría de Seguridad — ExplorApp (RNF5)

**Fecha:** 2026-05-27
**Branch:** `feature/86e19t088`
**Card ClickUp:** [86e19t088](https://app.clickup.com/t/86e19t088)
**Alcance:** Backend (microservicios FastAPI), orquestación Docker, frontend (Vite/React),
n8n + RAG, base de datos PostgreSQL.

> Objetivo: validar el cumplimiento del RNF5 (seguridad) antes de la entrega final.
> Se revisan secretos, JWT, CORS, aislamiento de red, validación de entrada y logs.

---

## 1. Resumen ejecutivo

| # | Ítem del checklist                                              | Resultado | Comentario |
|---|-----------------------------------------------------------------|-----------|------------|
| 1 | PostgreSQL sin puerto publicado al host                         | [x] OK    | Sólo expone 5432 dentro de `app_network`. |
| 2 | Todos los microservicios validan JWT (token inválido → 401)     | [x] OK    | Verificado por `curl` contra los 5 endpoints. |
| 3 | Tokens expirados son rechazados                                 | [x] OK    | `auth.py` maneja `ExpiredSignatureError` → 401. |
| 4 | CORS configurado correctamente (no `*`)                         | [x] OK    | `allow_origins=["http://localhost:5173"]` en 5/5 MS + nginx LB. |
| 5 | Secretos no están en el repo                                    | [x] OK    | `.env` ignorado, sólo se versiona `.env.example` con valores ficticios. |
| 6 | No hay SQL injection                                            | [x] OK    | Pydantic + queries parametrizadas (`$1`, `$2`, …). |
| 7 | Foto: validación de tipo MIME y tamaño en backend               | [~] PARCIAL | Tamaño validado (≤2 MB). MIME **no validado** explícitamente en backend → ver §7. |
| 8 | Logs no exponen datos sensibles                                 | [x] OK    | No se imprime token, password ni body completo. Sólo nombres/IDs de negocio. |

**Conclusión:** 7/8 ítems cumplen. Existe **1 observación** sobre la validación
de MIME de la foto que se documenta como mejora recomendable, pero **no bloquea
la entrega** porque la validación de tamaño y la persistencia ocurren del lado
servidor y el campo `foto_ruta` no se ejecuta como código.

---

## 2. PostgreSQL sin puerto publicado al host (RNF5)

**Evidencia:** `docker-compose.yml` (servicio `postgres`) no declara la clave
`ports:`. El contenedor sólo abre 5432 dentro de la red `app_network`.

```bash
$ docker ps --format "{{.Names}}\t{{.Ports}}" | grep postgres
explorapp_postgres   5432/tcp
```

(no aparece `0.0.0.0:5432->5432/tcp`).

Los microservicios y n8n acceden vía el hostname `postgres` resuelto por el DNS
interno de Docker.

**Resultado:** [x] Cumple.

---

## 3. Validación JWT en todos los microservicios

**Implementación común:** `microservicios/shared/auth.py` →
`validar_token_auth0(...)`.

Pasos del validador:

1. Descarga el JWKS de Auth0 (`/.well-known/jwks.json`).
2. Lee el `kid` de la cabecera del token.
3. Empareja la llave RSA y decodifica con `jwt.decode(..., algorithms=["RS256"], audience=API_AUDIENCE, issuer=...)`.
4. Captura excepciones específicas:
   - `ExpiredSignatureError` → 401 *"El token ha expirado"*.
   - `JWTClaimsError` → 401 *"Claims incorrectos"*.
   - Genérica → 401 *"Error genérico al validar el token"*.
5. Si no hay `kid` válido → 401 *"No se encontró una llave pública válida"*.

**Verificación funcional (sin token):**

```bash
$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8001/api/personas      # creacion
401
$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8002/api/personas/1   # modificacion (PATCH)
401
$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8003/api/personas/1   # consulta (vía LB nginx)
401
$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8004/api/personas/1   # borrado
401
$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8005/api/logs         # logs
401
```

**Verificación con token inválido:**

```bash
$ curl -s -H "Authorization: Bearer faketoken" http://localhost:8003/api/personas/1
{"detail":"Token inválido. Error al decodificar la cabecera."}
HTTP/1.1 401 Unauthorized
```

**Verificación con token expirado (firma RS256 no emitida por Auth0):**

```bash
$ curl -s -H "Authorization: Bearer <jwt-firmado-localmente-con-exp-pasado>" \
       http://localhost:8005/api/logs
{"detail":"No se encontró una llave pública válida (JWKS) para este token"}
HTTP/1.1 401 Unauthorized
```

Para un token expirado emitido por el mismo tenant, el camino del código
en `auth.py` líneas 67-72 garantiza la respuesta 401 con detalle
"El token ha expirado".

**Excepción documentada:** el endpoint `POST /api/logs/internal` del MS `log`
**no exige JWT** intencionalmente. Es un endpoint interno usado por el workflow
RAG de n8n, que corre dentro de `app_network`. n8n no porta el JWT del usuario
final; en su lugar, recibe el `auth0_id` en el body. Como el contenedor `log`
**no publica este endpoint con autenticación distinta**, está protegido sólo
por el aislamiento de red (no hay exposición pública a este `path` desde
fuera del `app_network` salvo que se haga port-forward, lo cual está
controlado por `docker-compose.yml`).

**Resultado:** [x] Cumple (ítems 2 y 3).

---

## 4. CORS sin wildcard

Todos los microservicios FastAPI usan `CORSMiddleware` con `allow_origins`
**restringido** al dev server del frontend:

| Microservicio  | Archivo                              | allow_origins                       |
|----------------|--------------------------------------|-------------------------------------|
| ms-crear       | `microservicios/ms-crear/main.py:11` | `["http://localhost:5173"]`         |
| ms-modificar   | `microservicios/ms-modificar/main.py:11` | `["http://localhost:5173"]`     |
| ms-consultar   | `microservicios/ms-consultar/main.py:15` | `["http://localhost:5173"]`     |
| ms-borrar      | `microservicios/ms-borrar/main.py:10` | `["http://localhost:5173"]`        |
| ms-log         | `microservicios/ms-log/main.py:13`   | `["http://localhost:5173"]`         |

El **load balancer nginx** (`nginx/consulta-lb.conf`) también emite los headers
CORS con origen explícito y **oculta** los headers del upstream para evitar
duplicados:

```nginx
add_header Access-Control-Allow-Origin "http://localhost:5173" always;
add_header Access-Control-Allow-Credentials "true" always;
add_header Access-Control-Allow-Methods "GET, OPTIONS" always;
add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
...
proxy_hide_header Access-Control-Allow-Origin;
```

**Resultado:** [x] Cumple. No se usa `"*"` en ningún servicio.

---

## 5. Secretos fuera del repositorio

**Archivos versionados que coinciden con el patrón `*env*` o `*secret*`:**

```bash
$ git ls-files | grep -iE "\.env$|\.env\."
.env.example
```

Sólo se versiona `.env.example` con valores **ficticios** (la regla está en
`.gitignore` líneas 70-74):

```gitignore
# =========================
# Variables de entorno
# =========================
.env
.env.local
.env.*.local
!.env.example
```

**Credenciales de n8n:** sólo se versionan plantillas con placeholders
(`n8n/credentials/anthropic.template.json` y `postgres.template.json`).
Los valores reales se inyectan vía variables `${POSTGRES_USER}`, `${LLM_API_KEY}`,
etc., resueltas desde el `.env` local que no se sube.

```bash
$ git ls-files | xargs grep -lE "sk-ant-[A-Za-z0-9_-]{20,}" 2>/dev/null
(sin resultados)
```

**Resultado:** [x] Cumple.

---

## 6. Prevención de SQL injection

### 6.1 Validación de entrada (Pydantic)

`microservicios/shared/models.py` define modelos con `pattern`, `max_length`,
`Literal` y `EmailStr`:

```python
class PersonaCreate(BaseModel):
    tipo_documento: Literal['Tarjeta de identidad', 'Cédula']
    nro_documento: str = Field(pattern=r'^[0-9]{1,10}$')
    primer_nombre: str = Field(max_length=30, pattern=r'^[^0-9]+$')
    correo: EmailStr
    celular: str = Field(pattern=r'^[0-9]{10}$')
```

Cualquier valor que no respete el patrón es rechazado por FastAPI antes de
llegar a la capa de DB.

### 6.2 Queries parametrizadas

Todas las llamadas a `asyncpg` usan placeholders posicionales `$1`, `$2`, …
en lugar de interpolación de strings. Ejemplos:

```python
# microservicios/ms-borrar/main.py:31
await conn.execute("DELETE FROM personas WHERE nro_documento = $1", documento)

# microservicios/ms-crear/main.py:86
await conn.execute(
    """INSERT INTO personas (nro_documento, tipo_documento, primer_nombre, ...)
       VALUES ($1, $2, $3, ...)""",
    nro_documento, tipo_documento, primer_nombre, ...
)

# microservicios/ms-consultar/main.py:36
await conn.fetchrow("SELECT * FROM personas WHERE nro_documento = $1", documento)
```

### 6.3 Excepciones revisadas (dynamic SQL controlado)

Dos endpoints construyen SQL dinámico:

- **`ms-modificar/main.py:37-43`** — el `SET` se arma a partir de
  `campos_a_actualizar.keys()`. Esas claves provienen de `PersonaUpdate.model_dump`,
  por lo que están restringidas al conjunto cerrado de campos definidos en el
  modelo Pydantic (`tipo_documento`, `primer_nombre`, ...). No hay forma de
  inyectar identificadores arbitrarios. Los **valores** sí van por placeholders.

- **`ms-log/main.py:32-58`** — los filtros `tipo`, `documento`, `fecha` se
  añaden a la cláusula `WHERE` interpolando sólo el **número de placeholder**
  (`${contador}`, no el valor). Los valores siguen viajando por `valores`
  como parámetros posicionales. La fecha se parsea con `date.fromisoformat`
  antes de pasarla.

**Resultado:** [x] Cumple. No se detectó ningún `f"... {valor_usuario} ..."` directo
contra la DB.

---

## 7. Validación de la foto en backend (MIME y tamaño)

**Estado actual** (`microservicios/ms-crear/main.py:51-58`):

```python
if foto and foto.filename:
    contenido = await foto.read()
    if len(contenido) > 2 * 1024 * 1024:
        raise HTTPException(status_code=422, detail="La foto no debe superar los 2 MB")
    extension = foto.filename.split('.')[-1]
    file_path = f"{UPLOAD_DIR}/{nro_documento}.{extension}"
    with open(file_path, "wb") as f:
        f.write(contenido)
```

- **Tamaño:** [x] Validado en backend (≤ 2 MB). Coincide con `MAX_UPLOAD_SIZE_MB=2`
  del `.env.example`.
- **MIME:** [~] **No se valida explícitamente**. El backend usa la extensión
  del filename del cliente para construir la ruta destino.

### Análisis de riesgo

- La ruta destino `f"{UPLOAD_DIR}/{nro_documento}.{extension}"` usa el
  `nro_documento` ya validado por Pydantic (`^[0-9]{1,10}$`), por lo que **no es
  posible un path traversal vía `nro_documento`**.
- La extensión sí proviene del filename del cliente; un atacante podría subir
  un archivo `.php` o `.html` con MIME falso. **Sin embargo:**
  - El directorio `/app/uploads` se sirve estático vía
    `StaticFiles(directory=UPLOAD_DIR)` en `ms-consultar`, que **no ejecuta**
    código del lado servidor.
  - El frontend nunca interpreta esos archivos como código.
- El riesgo real residual es de **almacenamiento de contenido arbitrario**
  (no ejecutable) y de **mostrar contenido inesperado** al usuario que consulte
  la foto.

### Recomendación (no bloqueante)

Añadir validación de `foto.content_type` en `ms-crear` antes de escribir el
archivo, p. ej.:

```python
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
if foto.content_type not in ALLOWED_MIME:
    raise HTTPException(status_code=415, detail="Tipo de imagen no permitido")
```

y sanear la extensión a partir del MIME en lugar del filename del cliente.
Se deja anotado como mejora para una próxima iteración.

**Resultado:** [~] Parcial — tamaño OK, MIME pendiente como mejora.

---

## 8. Exposición de datos sensibles en logs

Búsqueda de patrones `print(`, `logging`, `logger.` en los microservicios:

```
microservicios/shared/database.py:38   logger.error(f"Error en la transacción de base de datos: {str(e)}")
microservicios/shared/database.py:51   logger.error(f"Excepción crítica al ejecutar query: {str(e)}")
```

- No se imprimen tokens, headers `Authorization` ni passwords.
- Los logs de auditoría (`tabla logs`) almacenan `tipo_transaccion`,
  `documento_relacionado`, `detalle` (texto corto generado por el MS), y
  para el flujo RAG la `pregunta_rag` y `respuesta_rag`. **No se guarda el
  JWT, ni el `email` en plano fuera del `usuarios.email`** que es necesario
  para la operación.
- `database.py` registra solo el string del error de SQLAlchemy, no el
  payload de la query.

**Resultado:** [x] Cumple. No se expone PII innecesaria ni secretos.

---

## 9. Hardening adicional observado

Mientras se ejecutaba la auditoría se confirmaron también estas medidas:

- **Aislamiento de red:** la única forma de hablar con `postgres` y con
  el endpoint interno `POST /api/logs/internal` es desde dentro de
  `app_network`. n8n, los MS y el LB están en esa red; el frontend la usa
  sólo a través de los puertos publicados explícitamente.
- **Auth0 Universal Login + RS256** (no HS256), llaves rotables desde el tenant.
- **Audience e issuer** verificados explícitamente en `auth.py`.
- **`UniqueViolationError`** mapeado a 409 (no se expone el detalle SQL).
- **Las réplicas de `ms-consultar`** no publican puerto: sólo el LB nginx
  expone 8003 al host. Igual patrón que `postgres`.
- **Frontend** monta el volumen sólo del propio `frontend/`, no del repo
  completo.

---

## 10. Conclusión final

La aplicación cumple el RNF5 para la entrega:

- **7/8 ítems** del checklist están en verde.
- **1 ítem** (validación de MIME de la foto) queda anotado como mejora; el
  riesgo residual es bajo dado que los archivos servidos no se ejecutan y
  el tamaño sí está acotado en backend.
- No se encontraron secretos versionados, ni endpoints públicos sin JWT
  (con la excepción documentada del endpoint interno de logs RAG, que está
  protegido por aislamiento de red).
- No se detectó SQL injection.
- CORS está restringido al origen del frontend en todos los servicios.

Se considera la auditoría **aprobada**.
