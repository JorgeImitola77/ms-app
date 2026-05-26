# n8n — Motor de automatización y RAG

Esta carpeta contiene la configuración del contenedor **n8n** que actúa como
motor de automatización y soporte para el flujo RAG (Retrieval-Augmented
Generation) de ExplorApp.

## Estructura

- `workflows/` — Workflows exportados de n8n en formato JSON. Importar desde
  la UI de n8n (`Workflows → Import from File`) o vía la API.
- `credentials/` — Plantillas de credenciales que deben recrearse manualmente
  en cada entorno (no se versionan los secretos reales).
- `data/` — **No versionada**. Volumen persistente local de n8n
  (`/home/node/.n8n` dentro del contenedor, mapeado al volumen
  `explorapp_n8n_data`).

## Levantar n8n

n8n se inicia junto con el resto de servicios mediante:

```bash
docker compose up -d n8n
```

Una vez arriba, la UI queda disponible en
[http://localhost:5678](http://localhost:5678). Las credenciales de acceso son
las definidas en `.env` (`N8N_BASIC_AUTH_USER` / `N8N_BASIC_AUTH_PASSWORD`).

## Variables relevantes (ver `.env.example`)

- `N8N_HOST`, `N8N_PORT`, `N8N_PROTOCOL`, `NODE_ENV`
- `N8N_BASIC_AUTH_ACTIVE` (default `true`)
- `N8N_BASIC_AUTH_USER`, `N8N_BASIC_AUTH_PASSWORD`
- `WEBHOOK_URL` — URL pública para webhooks expuestos por n8n
- `GENERIC_TIMEZONE`
- `LLM_API_KEY` — clave del proveedor del LLM (OpenAI o equivalente)

## Configurar credenciales

Las credenciales no se cargan automáticamente porque n8n las cifra con la
encryption key del instance. Importarlas la primera vez desde la UI:

### 1) PostgreSQL (`ExplorApp Postgres`)

1. UI n8n → `Settings` → `Credentials` → `New` → tipo **Postgres**.
2. Completar con los valores de `n8n/credentials/postgres.template.json`:
   - Host: `postgres`  *(nombre del servicio en la red interna)*
   - Database: valor de `POSTGRES_DB`
   - User: valor de `POSTGRES_USER`
   - Password: valor de `POSTGRES_PASSWORD`
   - Port: `5432`
   - SSL: `disable`
3. Guardar con el nombre **`ExplorApp Postgres`**.

### 2) LLM (`ExplorApp LLM`)

El proyecto usa **Anthropic Claude** (modelo `claude-sonnet-4-6`), no OpenAI.

1. UI n8n → `Settings` → `Credentials` → `New` → tipo **Anthropic**.
2. Pegar como `API Key` el valor de `LLM_API_KEY` del `.env` (clave `sk-ant-...`).
3. Guardar con el nombre **`ExplorApp LLM`**.

## Importar el workflow de prueba

Para validar la conexión PostgreSQL:

1. UI n8n → `Workflows` → `Import from File` →
   seleccionar `n8n/workflows/test_personas.json`.
2. Abrir el nodo **Postgres - SELECT personas** y asignar la credencial
   `ExplorApp Postgres` (el campo `id` viene como placeholder).
3. Click en `Execute Workflow`.

### Criterio de aceptación

- [x] UI de n8n accesible en `http://localhost:5678` (con basic auth).
- [x] Workflow de prueba devuelve la primera fila de `personas`
      (`SELECT * FROM personas LIMIT 1`).
- [x] Credenciales `ExplorApp Postgres` y `ExplorApp LLM` guardadas y
      funcionales.

## Workflow RAG (`rag_consulta_personas.json`)

Implementa el patrón RAG (RF8 / Caso de Uso 3): responde consultas en lenguaje
natural sobre la tabla `personas` y registra cada consulta en el log de
auditoría.

### Flujo de nodos

1. **Webhook RAG** (`POST /webhook/rag-consulta`) — recibe
   `{ "pregunta": string, "usuario_id": string }`.
2. **Claude - Generar SQL** — Claude traduce la pregunta a un `SELECT` de
   PostgreSQL (NL2SQL) acotado al esquema de `personas`.
3. **Sanitizar SQL** — valida que sea un único `SELECT` (rechaza
   INSERT/UPDATE/DELETE/DDL y multi-sentencia); si no, usa `SELECT NULL AS error`.
4. **Postgres - Ejecutar SQL** — ejecuta la consulta con la credencial
   `ExplorApp Postgres`.
5. **Componer contexto** — agrupa las filas como contexto JSON.
6. **Claude - Generar Respuesta** — Claude redacta la respuesta natural a partir
   del contexto + la pregunta.
7. **Registrar Log** — `POST http://log:8000/api/logs/internal` con
   `tipo_transaccion=CONSULTA_RAG`, `pregunta_rag`, `respuesta_rag`, `usuario_id`.
   Tolera fallos (`continueRegularOutput`) para no romper la respuesta al usuario.
8. **Responder al Frontend** — devuelve `{ "pregunta", "respuesta" }`.

### Importar y configurar

1. UI n8n → `Workflows` → `Import from File` →
   `n8n/workflows/rag_consulta_personas.json`.
2. Asignar la credencial `ExplorApp Postgres` al nodo **Postgres - Ejecutar SQL**.
3. Asignar la credencial `ExplorApp LLM` (Anthropic) a **ambos** nodos
   `Claude - *` (el campo `id` viene como placeholder).
4. Guardar y **activar** el workflow para exponer el webhook productivo.

### Probar (`curl`)

```bash
curl -X POST http://localhost:5678/webhook/rag-consulta \
  -H "Content-Type: application/json" \
  -d '{"pregunta":"¿Cuál es el empleado más joven?","usuario_id":null}'
```

### Casos de prueba

- `"¿Cuál es el empleado más joven?"` → devuelve el nombre.
- `"¿Cuántas personas hay registradas?"` → devuelve el conteo.
- `"Lista las personas cuyo género sea No binario."` → devuelve la lista.

### Criterio de aceptación

- [x] Webhook responde con la respuesta natural a las 3 preguntas de prueba.
- [x] Cada consulta queda registrada en `logs` con
      `tipo_transaccion = CONSULTA_RAG` (verificable vía `GET /api/logs?tipo=CONSULTA_RAG`).
- [x] Workflow exportado a JSON y versionado en `n8n/workflows/`.
