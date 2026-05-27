# ExplorApp — Sistema de Gestión de Personal

Monorepo del proyecto **ExplorApp**, desarrollado para la asignatura de
**Diseño de Software 2** (Universidad del Norte). El sistema
permite registrar, consultar, modificar y eliminar personas, con auditoría
completa de transacciones y un motor de automatización basado en n8n + RAG.

La arquitectura sigue un patrón de **microservicios** desplegados con Docker
Compose, una **base de datos PostgreSQL** compartida, un **frontend React +
Vite + Tailwind** y un cliente móvil Android que se autentica vía **Auth0**.

---

## Tabla de contenidos

- [Arquitectura](#arquitectura)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Requisitos previos](#requisitos-previos)
- [Puesta en marcha](#puesta-en-marcha)
- [Endpoints y puertos](#endpoints-y-puertos)
- [Base de datos](#base-de-datos)
- [Convenciones de Git](#convenciones-de-git)
- [Equipo](#equipo)

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
   ┌─────────────────────────────────────────────────┐
   │           Capa de microservicios FastAPI         │
   │  ms-crear · ms-modificar · ms-consultar          │
   │  ms-borrar · ms-log                              │
   └────────────┬─────────────────────┬──────────────┘
                │                     │
                ▼                     ▼
        ┌──────────────┐       ┌──────────────┐
        │  PostgreSQL  │◀──────│     n8n      │
        │              │       │  (RAG/Auto.) │
        └──────────────┘       └──────────────┘
```

Cada microservicio tiene una única responsabilidad (CRUD + log) y expone su
propia imagen Docker. La separación facilita escalar el servicio de
**consulta** de forma independiente.

---

## Estructura del repositorio

```
ms-app/
├── frontend/                # React + Vite + Tailwind
│   ├── src/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
├── microservicios/
│   ├── ms-crear/            # POST /api/personas
│   ├── ms-modificar/        # PUT/PATCH /api/personas
│   ├── ms-consultar/        # GET /api/personas (escalable)
│   ├── ms-borrar/           # DELETE /api/personas
│   └── ms-log/              # API de auditoría
├── n8n/                     # Configuración del motor RAG
│   ├── workflows/
│   └── credentials/
├── db/
│   └── init.sql             # Migraciones iniciales
├── uploads/                 # Fotos de personas (volumen Docker)
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```



---

## Requisitos previos

- **Docker Desktop** ≥ 24
- **Docker Compose** v2
- **Node.js** ≥ 18 y **npm** ≥ 9 (solo si se desarrolla el frontend fuera de
  Docker)
- **Python** ≥ 3.11 (solo si se desarrolla un microservicio fuera de Docker)
- Cuenta de **Auth0** para emitir tokens JWT desde la app Android

---

## Puesta en marcha

1. **Clonar el repositorio**

   ```bash
   git clone <url-del-repo>
   cd ms-app
   ```

2. **Configurar variables de entorno**

   ```bash
   cp .env.example .env
   ```

   Editar `.env` y completar las credenciales reales (DB, Auth0, n8n).

3. **Levantar toda la infraestructura**

   ```bash
   docker compose up --build
   ```

   En el primer arranque, PostgreSQL ejecuta `db/init.sql` para crear las
   tablas `personas` y `logs`.

4. **Frontend (modo desarrollo, opcional)**

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Disponible en [http://localhost:5173](http://localhost:5173).

---

## Endpoints y puertos

| Servicio       | Puerto host | Puerto contenedor | Función                       |
|----------------|-------------|-------------------|-------------------------------|
| PostgreSQL     | 5432        | 5432              | Base de datos principal       |
| ms-crear       | 8001        | 8000              | `POST /api/personas`          |
| ms-modificar   | 8002        | 8000              | `PUT/PATCH /api/personas`     |
| ms-consultar   | 8003        | 8000              | `GET /api/personas`           |
| ms-borrar      | 8004        | 8000              | `DELETE /api/personas`        |
| ms-log         | 8005        | 8000              | `GET /api/logs` (auditoría)   |
| n8n            | 5678        | 5678              | Motor de automatización + RAG |

Todos los microservicios validan el JWT emitido por Auth0 antes de ejecutar
operaciones contra la base de datos.

---

## Base de datos

El esquema inicial vive en [`db/init.sql`](db/init.sql) y se ejecuta
automáticamente al crear el volumen de Postgres:

- **`personas`** — datos personales (PK: `nro_documento`).
- **`logs`** — auditoría de cada transacción (CRUD).

Las migraciones futuras se añaden como nuevos archivos `db/NN_<descripcion>.sql`.

---

## Convenciones de Git

- **Branch principal:** `main` (protegido — sin push directo).
- **Branches de trabajo:** `feature/<id-card>/<descripcion-corta>` para
  features y `fix/<id-card>/<descripcion-corta>` para correcciones, donde
  `<id-card>` es el ID de la card de ClickUp asociada.
- **Pull requests:** requieren al menos una revisión y que el pipeline de CI
  pase antes de hacer merge.
- **Mensajes de commit:** breves, en español, en presente
  (p. ej. `agrega validación de foto en ms-crear`).

---

## Equipo

| Nombre                       | Rol                       | 
|------------------------------|---------------------------|
| Verónica Ospina Monsalve     | DevOps          |
| Hernando Boris Barreto Arenas      | DevOps               | 
| Jorge Imitola       | DevOps              | 
| Zenen Contreras       | DevOps              | 



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
