# ExplorApp — Sistema de Gestión de Personal

> Proyecto académico desarrollado para la asignatura **Diseño de Software 2**
> de la **Universidad del Norte**, bajo la dirección del profesor
> **Pierre Julliard**.

ExplorApp es un sistema de gestión de personas (CRUD + auditoría) construido
sobre una arquitectura de **microservicios** desplegados con Docker Compose.
Cuenta con un **frontend web** en React + Vite + Tailwind, un cliente Android
que se autentica vía **Auth0**, y un motor de automatización en **n8n** que
expone un workflow **RAG** (Retrieval-Augmented Generation) sobre la base de
datos PostgreSQL.

---

## Tabla de contenidos

- [Equipo y asignatura](#equipo-y-asignatura)
- [Descripción del sistema](#descripción-del-sistema)
- [Stack tecnológico](#stack-tecnológico)
- [Arquitectura](#arquitectura)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Requisitos previos](#requisitos-previos)
- [Puesta en marcha](#puesta-en-marcha)
- [Variables de entorno](#variables-de-entorno)
- [Endpoints y documentación (Swagger / OpenAPI)](#endpoints-y-documentación-swagger--openapi)
- [Cómo correr los tests](#cómo-correr-los-tests)
- [Cómo escalar el servicio de Consulta](#cómo-escalar-el-servicio-de-consulta)
- [Base de datos](#base-de-datos)
- [Troubleshooting común](#troubleshooting-común)
- [Convenciones de Git](#convenciones-de-git)
- [Evidencia de pruebas E2E](#evidencia-de-pruebas-e2e)
- [Licencia](#licencia)

---

## Equipo y asignatura



### Integrantes

| Nombre                          | Rol     |
|---------------------------------|---------|
| Verónica Ospina Monsalve        | DevOps  |
| Hernando Boris Barreto Arenas   | DevOps  |
| Jorge Imitola                   | DevOps  |
| Zenen Contreras                 | DevOps  |

---

## Descripción del sistema

ExplorApp permite a un operador autenticado:

- **Registrar** una persona con sus datos básicos y foto.
- **Consultar** personas con filtros y paginación.
- **Modificar** los datos de una persona existente.
- **Eliminar** una persona (con auditoría).
- **Auditar** las transacciones desde un microservicio de logs.
- **Conversar** con un asistente RAG (n8n + Anthropic Claude) que responde
  consultas en lenguaje natural sobre los datos almacenados.

Cada operación CRUD reside en su propio microservicio FastAPI, lo que permite
escalar de forma independiente las operaciones más demandadas (consulta) y
aislar fallos.

---

## Stack tecnológico

| Capa            | Tecnología                                                          |
|-----------------|---------------------------------------------------------------------|
| Frontend        | React 18, Vite 5, TailwindCSS 3, React Router 6, Auth0 React SDK    |
| Backend         | Python 3.11+, FastAPI, Uvicorn, Pydantic 2, asyncpg, SQLAlchemy     |
| Autenticación   | Auth0 (JWT RS256)                                                   |
| Base de datos   | PostgreSQL 15 (imagen `pgvector/pgvector:pg15` para soporte RAG)    |
| Automatización  | n8n + Anthropic Claude (workflow RAG)                               |
| Balanceo        | NGINX 1.27 (load balancer del servicio Consulta)                    |
| Orquestación    | Docker + Docker Compose v2                                          |
| Pruebas         | pytest, pytest-asyncio, pytest-cov, httpx, Locust (carga)           |

---

## Arquitectura

```
        ┌──────────────┐         ┌──────────────────┐
        │   Frontend   │         │   App Android    │
        │ React + Vite │         │     (Auth0)      │
        └──────┬───────┘         └─────────┬────────┘
               │   HTTP/REST              │ JWT
               └────────────┬─────────────┘
                            ▼
        ┌────────────────────────────────────────────┐
        │   ms-crear   ms-modificar   ms-borrar      │
        │   ms-log         consulta-lb (nginx)       │
        │                       │                    │
        │                       ▼                    │
        │              ms-consultar  x N réplicas    │
        └────────────┬─────────────────────┬─────────┘
                     │                     │
                     ▼                     ▼
             ┌──────────────┐       ┌──────────────┐
             │  PostgreSQL  │◀──────│     n8n      │
             │  (pgvector)  │       │  (RAG/Auto.) │
             └──────────────┘       └──────────────┘
```

Notas clave de diseño:

- **PostgreSQL no publica puerto al host** (RNF5): solo es accesible a través
  de la red interna `explorapp_app_network`.
- **`ms-consultar` no se expone directamente**: el tráfico entra por
  `consulta-lb` (NGINX) en el puerto `8003`, que hace round-robin entre las N
  réplicas levantadas con `--scale consulta=N` (RNF3).
- Todos los microservicios validan el **JWT emitido por Auth0** antes de
  ejecutar operaciones contra la base de datos.

---

## Estructura del repositorio

```
ms-app/
├── frontend/                # React + Vite + Tailwind
│   ├── src/
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── microservicios/
│   ├── ms-crear/            # POST /api/personas
│   ├── ms-modificar/        # PUT/PATCH /api/personas
│   ├── ms-consultar/        # GET /api/personas (escalable)
│   ├── ms-borrar/           # DELETE /api/personas
│   ├── ms-log/              # GET /api/logs (auditoría)
│   ├── shared/              # Módulos compartidos (auth, models, errores)
│   └── tests/               # Suite pytest de todos los microservicios
├── n8n/                     # Workflows y credenciales del motor RAG
│   ├── workflows/
│   └── credentials/
├── nginx/
│   └── consulta-lb.conf     # Load balancer del servicio Consulta
├── db/
│   └── init.sql             # Esquema y datos iniciales
├── loadtest/                # Escenarios Locust de carga
├── docs/                    # auth0-setup, error-handling, evidencias-e2e
├── uploads/                 # Volumen Docker para fotos
├── docker-compose.yml
├── .env.example
├── test.bat                 # Menú interactivo de tests (Windows)
└── README.md
```

---

## Requisitos previos

| Herramienta        | Versión mínima | Notas                                       |
|--------------------|---------------:|---------------------------------------------|
| Docker Desktop     |             24 | Incluye Docker Compose v2                   |
| Docker Compose     |             v2 | `docker compose ...`                        |
| Cuenta Auth0       |              — | Para emitir JWT desde la app web y Android  |
| Node.js (opcional) |             18 | Solo si se desarrolla el frontend fuera de Docker |
| Python  (opcional) |           3.11 | Solo para correr tests fuera de Docker      |

> El profesor solo necesita **Docker Desktop** y **una cuenta Auth0** (o usar
> las credenciales de prueba incluidas en `.env.example`) para levantar el
> sistema completo.

---

## Puesta en marcha

1. **Clonar el repositorio**

   ```bash
   git clone <url-del-repo>
   cd ms-app
   ```

2. **Configurar las variables de entorno**

   ```bash
   cp .env.example .env
   ```

   Editar `.env` y completar los valores reales (ver
   [Variables de entorno](#variables-de-entorno)).

3. **Levantar toda la infraestructura**

   ```bash
   docker compose up --build
   ```

   En el primer arranque, PostgreSQL ejecuta `db/init.sql` para crear las
   tablas `personas` y `logs`. Esperar a que todos los contenedores estén en
   estado `healthy` (≈ 30 s).

4. **Abrir el frontend**

   [http://localhost:5173](http://localhost:5173)

5. **Acceder a n8n** (opcional, para gestionar el workflow RAG)

   [http://localhost:5678](http://localhost:5678) (basic auth con las
   credenciales `N8N_BASIC_AUTH_USER` / `N8N_BASIC_AUTH_PASSWORD` del `.env`).

### Apagar el stack

```bash
docker compose down            # Conserva los volúmenes (datos persistidos)
docker compose down -v         # Borra también pg_data, photos y n8n_data
```

---

## Variables de entorno

Todas las variables se cargan desde el archivo `.env` en la raíz. A
continuación se explica cada bloque:

### Base de datos PostgreSQL

| Variable            | Ejemplo                                                | Descripción                              |
|---------------------|--------------------------------------------------------|------------------------------------------|
| `POSTGRES_USER`     | `admin`                                                | Usuario administrador de la DB           |
| `POSTGRES_PASSWORD` | `password123`                                          | Contraseña del usuario                   |
| `POSTGRES_DB`       | `personasdb`                                           | Nombre de la base de datos               |
| `POSTGRES_HOST`     | `postgres`                                             | Hostname interno (nombre del servicio)   |
| `POSTGRES_PORT`     | `5432`                                                 | Puerto interno                           |
| `DATABASE_URL`      | `postgresql://admin:password123@postgres:5432/personasdb` | URL completa usada por los microservicios |

### Auth0

| Variable                    | Descripción                                                |
|-----------------------------|------------------------------------------------------------|
| `AUTH0_DOMAIN`              | Dominio del tenant Auth0 (`*.us.auth0.com`)                |
| `AUTH0_CLIENT_ID`           | Client ID de la aplicación SPA                             |
| `AUTH0_AUDIENCE`            | Audience de la API protegida (`https://api.explorapp`)     |
| `AUTH0_ALGORITHMS`          | `RS256`                                                    |
| `AUTH0_CLIENT_SECRET`       | Secret del backend (requerido por la rúbrica)              |
| `VITE_AUTH0_DOMAIN`         | Mismo dominio, expuesto al frontend Vite                   |
| `VITE_AUTH0_CLIENT_ID`      | Mismo Client ID, expuesto al frontend Vite                 |
| `VITE_AUTH0_AUDIENCE`       | Misma audience, expuesta al frontend Vite                  |

Ver [`docs/auth0-setup.md`](docs/auth0-setup.md) para el paso a paso de
creación del tenant, la API y la aplicación.

### n8n y RAG

| Variable                  | Descripción                                                  |
|---------------------------|--------------------------------------------------------------|
| `N8N_HOST`                | Host público de n8n (`localhost` en local)                   |
| `N8N_PORT`                | Puerto interno de n8n (`5678`)                               |
| `N8N_PROTOCOL`            | `http` en local, `https` en producción                       |
| `N8N_BASIC_AUTH_ACTIVE`   | `true` para exigir credenciales al abrir n8n                 |
| `N8N_BASIC_AUTH_USER`     | Usuario de basic auth                                        |
| `N8N_BASIC_AUTH_PASSWORD` | Contraseña de basic auth                                     |
| `WEBHOOK_URL`             | URL pública usada por n8n para registrar webhooks            |
| `GENERIC_TIMEZONE`        | Zona horaria (`America/Bogota`)                              |
| `LLM_API_KEY`             | API key de Anthropic Claude (`sk-ant-...`) usada por el RAG  |
| `VITE_N8N_RAG_URL`        | URL del webhook RAG consumida desde el frontend              |

### Servicio y almacenamiento

| Variable             | Descripción                                                      |
|----------------------|------------------------------------------------------------------|
| `UPLOAD_DIR`         | Ruta dentro del contenedor donde se almacenan las fotos          |
| `MAX_UPLOAD_SIZE_MB` | Tamaño máximo permitido para la foto (default 2 MB)              |
| `PHOTOS_VOLUME_PATH` | Path del volumen Docker para fotos (requerido por la rúbrica)    |
| `LOG_SERVICE_URL`    | URL interna del microservicio de logs (`http://ms-log:8005`)     |

### Puertos publicados al host

| Variable                  | Default | Servicio                  |
|---------------------------|--------:|---------------------------|
| `FRONTEND_PORT`           |    5173 | Frontend Vite             |
| `MS_CREACION_PORT`        |    8001 | ms-crear                  |
| `MS_MODIFICACION_PORT`    |    8002 | ms-modificar              |
| `MS_CONSULTA_PORT`        |    8003 | consulta-lb (NGINX)       |
| `MS_BORRADO_PORT`         |    8004 | ms-borrar                 |
| `MS_LOG_PORT`             |    8005 | ms-log                    |
| `N8N_PUBLIC_PORT`         |    5678 | n8n                       |

---

## Endpoints y documentación (Swagger / OpenAPI)

Cada microservicio FastAPI expone automáticamente su documentación
interactiva en `/docs` (Swagger UI) y su esquema OpenAPI en `/openapi.json`.

| Servicio       | Puerto host | Swagger UI                          | OpenAPI JSON                              |
|----------------|------------:|-------------------------------------|-------------------------------------------|
| ms-crear       | 8001        | http://localhost:8001/docs          | http://localhost:8001/openapi.json        |
| ms-modificar   | 8002        | http://localhost:8002/docs          | http://localhost:8002/openapi.json        |
| ms-consultar   | 8003        | http://localhost:8003/docs          | http://localhost:8003/openapi.json        |
| ms-borrar      | 8004        | http://localhost:8004/docs          | http://localhost:8004/openapi.json        |
| ms-log         | 8005        | http://localhost:8005/docs          | http://localhost:8005/openapi.json        |

Resumen de endpoints principales (todos requieren `Authorization: Bearer <JWT>`):

| Método  | Endpoint                       | Servicio       | Descripción                          |
|---------|--------------------------------|----------------|--------------------------------------|
| `POST`  | `/api/personas`                | ms-crear       | Crear una persona (multipart + foto) |
| `PUT`   | `/api/personas/{nro_documento}`| ms-modificar   | Actualizar datos completos           |
| `PATCH` | `/api/personas/{nro_documento}`| ms-modificar   | Actualizar campos parciales          |
| `GET`   | `/api/personas`                | ms-consultar   | Listar / filtrar personas            |
| `GET`   | `/api/personas/{nro_documento}`| ms-consultar   | Obtener una persona                  |
| `GET`   | `/uploads/{archivo}`           | ms-consultar   | Servir fotos almacenadas             |
| `DELETE`| `/api/personas/{nro_documento}`| ms-borrar      | Eliminar una persona                 |
| `GET`   | `/api/logs`                    | ms-log         | Consultar auditoría (filtros)        |

---

## Cómo correr los tests

### Opción 1 — menú interactivo (Windows)

En la raíz del repositorio existe `test.bat`, un menú interactivo que permite
correr toda la suite, generar reporte de coverage, filtrar por microservicio
o ejecutar las pruebas de carga con Locust:

```cmd
test.bat
```

La primera vez es necesario crear el entorno virtual de pruebas:

```cmd
py -3.13 -m venv .venv-test
.venv-test\Scripts\python.exe -m pip install fastapi==0.115.12 pydantic==2.11.1 ^
   "pydantic[email]" httpx==0.28.1 pytest==9.0.3 pytest-asyncio pytest-cov ^
   python-jose passlib bcrypt python-multipart asyncpg sqlalchemy
.venv-test\Scripts\python.exe -m pip install -r loadtest\requirements.txt
```

### Opción 2 — pytest directamente

```bash
# Todos los tests
pytest microservicios

# Con coverage
pytest microservicios --cov --cov-report=term-missing

# Solo un microservicio
pytest microservicios/tests/test_ms_crear.py -v

# Filtrar por nombre
pytest microservicios -k "modificar and not foto"
```

### Opción 3 — pruebas de carga con Locust

```bash
# Crear: 50 usuarios x 1 min
locust -f loadtest/locustfile.py --headless -u 50 -r 10 --run-time 1m CrearUser

# Consulta escalada: 100 usuarios x 1 min (levantar antes 3 réplicas)
docker compose up -d --scale consulta=3
locust -f loadtest/locustfile.py --headless -u 100 -r 20 --run-time 1m ConsultarUser

# RAG: 20 usuarios x 1 min
locust -f loadtest/locustfile.py --headless -u 20 -r 5 --run-time 1m RagUser
```

> Los endpoints autenticados requieren un JWT válido en la variable de
> entorno `LOADTEST_TOKEN`. Ver `loadtest/README.md` para generar el token.

---

## Cómo escalar el servicio de Consulta

El microservicio `consulta` está diseñado para escalar horizontalmente. El
contenedor `consulta-lb` (NGINX) recibe el tráfico en el puerto `8003` del
host y reparte las peticiones por **round-robin** entre todas las réplicas
mediante el DNS interno de Docker.

```bash
# Levantar 3 réplicas de consulta
docker compose up -d --scale consulta=3

# Subir a 5 réplicas en caliente, sin tocar los demás servicios
docker compose up -d --scale consulta=5

# Volver a 1 réplica
docker compose up -d --scale consulta=1
```

Verificación rápida:

```bash
# Listar las réplicas activas
docker compose ps consulta

# Ver el balanceo en acción (cada request debería ir a un contenedor distinto)
for i in 1 2 3 4 5; do curl -s http://localhost:8003/health; echo; done
```

Si todas las réplicas están apagadas, `consulta-lb` devuelve un **HTTP 503**
con un cuerpo JSON amigable, en lugar de un error técnico:

```json
{"detail": "El servicio de consulta no está disponible en este momento. Intenta de nuevo en unos segundos."}
```

> El servicio `consulta` no publica puertos directamente: por diseño, todo el
> tráfico externo pasa por `consulta-lb` (RNF3 / RNF5).

---

## Base de datos

El esquema inicial vive en [`db/init.sql`](db/init.sql) y se ejecuta
automáticamente al crear el volumen `pg_data`:

- **`personas`** — datos personales (PK: `nro_documento`).
- **`logs`** — auditoría de cada transacción CRUD y de cada consulta RAG.

La imagen usada es `pgvector/pgvector:pg15`, que añade soporte para vectores
y es consumida por el workflow RAG de n8n.

Para conectarse manualmente desde el host (con `psql` o un cliente gráfico):

```bash
# Abre un shell dentro del contenedor de PostgreSQL
docker compose exec postgres psql -U admin -d personasdb
```

> Recordatorio: el contenedor `postgres` **no** publica el puerto 5432 al
> host por seguridad (RNF5).

---

## Troubleshooting común

| Síntoma                                                              | Causa probable                                              | Solución                                                                                       |
|----------------------------------------------------------------------|-------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| `docker compose up` falla con `bind: address already in use`         | Otro proceso usa el puerto (5173, 8001–8005, 5678, etc.)    | Cambia el puerto en `.env` (p. ej. `FRONTEND_PORT=5174`) o detén el proceso que lo ocupa.       |
| El frontend muestra "Cannot connect to API" o errores CORS           | Auth0 no devolvió token o `.env` del frontend mal configurado | Verifica `VITE_AUTH0_*` y que la audience coincida con la API en Auth0.                        |
| `503` al hacer `GET /api/personas`                                   | No hay réplicas de `consulta` corriendo                     | `docker compose up -d --scale consulta=1` (o más).                                              |
| Los microservicios reinician con `connection refused` a PostgreSQL   | PostgreSQL aún no terminó de inicializar `init.sql`         | Espera ~30 s al primer arranque. Verifica `docker compose logs postgres`.                       |
| `401 Unauthorized` en todos los endpoints                            | JWT inválido, expirado o sin la audience correcta           | Vuelve a iniciar sesión. Revisa que el token contenga `aud=https://api.explorapp`.              |
| n8n no responde al webhook RAG                                       | Workflow no importado o `LLM_API_KEY` ausente               | Importa `n8n/workflows/*.json` desde la UI y verifica la API key en `.env`.                     |
| Cambios en el `.env` no aplican                                      | Docker Compose cacheó las variables                         | `docker compose down && docker compose up --build`.                                              |
| Foto no aparece al consultar una persona                             | Volumen `photos` desincronizado o ruta incorrecta           | `docker compose down -v` (⚠ borra datos) y vuelve a `up --build`.                                |
| Tests fallan con `ModuleNotFoundError: shared`                       | `PYTHONPATH` no incluye `microservicios/`                   | Corre pytest desde la raíz del repo: `pytest microservicios`.                                   |

Logs útiles:

```bash
docker compose logs -f frontend
docker compose logs -f consulta
docker compose logs -f postgres
docker compose logs -f n8n
```

---

## Convenciones de Git

- **Branch principal:** `main` (protegido — sin push directo).
- **Branches de trabajo:**
  - `feature/<id-card>/<descripcion-corta>` para features.
  - `fix/<id-card>/<descripcion-corta>` para correcciones.
  - `<id-card>` es el ID de la card de ClickUp asociada.
- **Pull requests:** requieren al menos una revisión y que el pipeline de CI
  pase antes de hacer merge.
- **Mensajes de commit:** breves, en español, en presente
  (p. ej. `agrega validación de foto en ms-crear`).

---

## Evidencia de pruebas E2E

Las pruebas end-to-end de los tres casos de uso definidos en la sección 10
del documento de diseño están documentadas en
[`docs/evidencias-e2e/README.md`](docs/evidencias-e2e/README.md), con
screenshots, consultas SQL de verificación y veredicto por caso.

---

## Licencia

Proyecto académico desarrollado en la Universidad del Norte. Uso restringido
al curso de Diseño de Software 2.
