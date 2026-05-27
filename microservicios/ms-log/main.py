import os
from fastapi import FastAPI, HTTPException, status, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import asyncpg
from schemas import LogOut, LogRagIn
from shared.auth import validar_token_auth0
from shared.errors import raise_for_unexpected, is_db_connection_error, DB_UNAVAILABLE_MSG
from datetime import date

# ---------------------------------------------------------------------------
# Configuración de la aplicación
# ---------------------------------------------------------------------------
_TAGS = [
    {
        "name": "Logs",
        "description": (
            "Consulta del **historial de transacciones** de auditoría. "
            "Soporta filtros por tipo de operación, número de documento y fecha."
        ),
    },
    {
        "name": "Interno",
        "description": (
            "Endpoints de uso **exclusivo desde la red privada** (`app_network`). "
            "Utilizados por el workflow RAG de n8n para registrar consultas de IA. "
            "No requieren JWT."
        ),
    },
]

_DESCRIPTION = """
## Microservicio Logs — ExplorApp

Responsable del **registro y consulta de auditoría** de todas las transacciones del sistema.

### Tipos de transacción registrados

| Tipo | Generado por |
|---|---|
| `CREAR` | ms-crear al registrar una persona |
| `CONSULTAR` | ms-consultar al buscar una persona |
| `MODIFICAR` | ms-modificar al actualizar datos |
| `BORRAR` | ms-borrar al eliminar un registro |
| `CONSULTA_RAG` | Workflow n8n al procesar una consulta de IA |

### Endpoints públicos (requieren JWT)
- `GET /api/logs` — lista todos los logs con filtros opcionales.

### Endpoints internos (sin JWT, solo red privada)
- `POST /api/logs/internal` — usado por n8n para registrar consultas RAG.

### Autenticación
Los endpoints protegidos requieren el encabezado:
```
Authorization: Bearer <access_token>
```
El token se obtiene desde Auth0 con el audience `https://api.explorapp`.
"""

app = FastAPI(
    title="MS-Log · ExplorApp",
    description=_DESCRIPTION,
    version="1.0.0",
    openapi_tags=_TAGS,
    contact={"name": "Equipo ExplorApp", "email": "zenencontreras1@gmail.com"},
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")


async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}


@app.get(
    "/api/logs",
    tags=["Logs"],
    summary="Consultar historial de transacciones",
    description="""
Devuelve la lista de entradas de auditoría ordenadas de la más reciente a la más antigua.

### Filtros disponibles (query params, todos opcionales)

| Parámetro | Descripción | Ejemplo |
|---|---|---|
| `tipo` | Filtra por tipo de transacción | `CREAR`, `CONSULTAR`, `MODIFICAR`, `BORRAR`, `CONSULTA_RAG` |
| `documento` | Filtra por número de documento relacionado | `1003377298` |
| `fecha` | Filtra por fecha exacta de la transacción | `2025-05-26` (formato `YYYY-MM-DD`) |

Los filtros se pueden combinar libremente. Sin filtros devuelve **todos los registros**.

### Sobre el campo `email_usuario`
Se obtiene mediante un `LEFT JOIN` con la tabla `usuarios`. Si el usuario no tiene email registrado, el campo es `null`.
""",
    response_model=List[LogOut],
    status_code=status.HTTP_200_OK,
    response_description="Lista de entradas de auditoría, ordenadas por fecha descendente.",
    responses={
        200: {
            "description": "Lista de logs.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id_log": 42,
                            "usuario_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "email_usuario": "hbbarreto@uninorte.edu.co",
                            "fecha_transaccion": "2025-05-26T14:30:00",
                            "tipo_transaccion": "CREAR",
                            "documento_relacionado": "1003377298",
                            "pregunta_rag": None,
                            "respuesta_rag": None,
                            "detalle": "Creación exitosa de Zenen Contreras Royero",
                        },
                        {
                            "id_log": 43,
                            "usuario_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "email_usuario": "hbbarreto@uninorte.edu.co",
                            "fecha_transaccion": "2025-05-26T15:10:00",
                            "tipo_transaccion": "CONSULTA_RAG",
                            "documento_relacionado": None,
                            "pregunta_rag": "Cuantas personas hay registradas?",
                            "respuesta_rag": "Hay 5 personas registradas en el sistema.",
                            "detalle": "RAG: 1 fila(s) | SQL: SELECT COUNT(*) FROM personas",
                        },
                    ]
                }
            },
        },
        400: {
            "description": "El parámetro `fecha` tiene un formato inválido.",
            "content": {
                "application/json": {
                    "example": {"detail": "Formato de fecha inválido. Usa YYYY-MM-DD."}
                }
            },
        },
        401: {
            "description": "Token ausente, inválido o expirado.",
            "content": {"application/json": {"example": {"detail": "El token ha expirado"}}},
        },
        503: {
            "description": "Base de datos no disponible.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "La base de datos no está disponible en este momento."
                    }
                }
            },
        },
    },
)
async def consultar_logs(
    tipo: Optional[str] = Query(
        None,
        description="Filtra por tipo de transacción. Valores: `CREAR`, `CONSULTAR`, `MODIFICAR`, `BORRAR`, `CONSULTA_RAG`.",
        example="CREAR",
    ),
    documento: Optional[str] = Query(
        None,
        description="Filtra por número de documento relacionado con la transacción.",
        example="1003377298",
    ),
    fecha: Optional[str] = Query(
        None,
        description="Filtra por fecha de la transacción en formato `YYYY-MM-DD`.",
        example="2025-05-26",
    ),
    token_payload: dict = Depends(validar_token_auth0),
):
    try:
        conn = await get_db_connection()
    except Exception as exc:
        if is_db_connection_error(exc):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=DB_UNAVAILABLE_MSG,
            )
        raise_for_unexpected(exc)

    try:
        query = """
            SELECT l.*, u.email AS email_usuario
            FROM logs l
            LEFT JOIN usuarios u ON l.usuario_id = u.usuario_id
            WHERE 1=1"""
        valores = []
        contador = 1

        if tipo:
            query += f" AND tipo_transaccion = ${contador}"
            valores.append(tipo)
            contador += 1

        if documento:
            query += f" AND documento_relacionado = ${contador}"
            valores.append(documento)
            contador += 1

        if fecha:
            query += f" AND DATE(fecha_transaccion) = ${contador}"
            try:
                fecha_obj = date.fromisoformat(fecha)
                valores.append(fecha_obj)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail="Formato de fecha inválido. Usa YYYY-MM-DD."
                )
            contador += 1

        query += " ORDER BY fecha_transaccion DESC"
        registros = await conn.fetch(query, *valores)

        return [dict(r) for r in registros]

    except HTTPException:
        raise
    except Exception as exc:
        raise_for_unexpected(exc)
    finally:
        await conn.close()


@app.post(
    "/api/logs/internal",
    tags=["Interno"],
    summary="Registrar log de consulta RAG (uso interno)",
    description="""
Endpoint **exclusivo de la red privada** `app_network`. Es invocado por el workflow RAG de n8n
al finalizar una consulta de inteligencia artificial.

**No requiere JWT.** El usuario se identifica mediante el campo `auth0_id` (el `sub` del token
que el frontend pasa al workflow de n8n en el cuerpo de la petición).

### Resolución del usuario
- Si se envía `usuario_id` (UUID), se usa directamente.
- Si se envía `auth0_id`, el servicio resuelve el UUID haciendo un `SELECT` en la tabla `usuarios`.
- Si el usuario no existe todavía, se **auto-registra** con el `auth0_id` y `email` provistos.

### Campos guardados
- `tipo_transaccion`: siempre `CONSULTA_RAG`
- `pregunta_rag`: la pregunta en lenguaje natural
- `respuesta_rag`: la respuesta generada por el LLM
- `detalle`: resumen de filas obtenidas y SQL ejecutado
""",
    status_code=status.HTTP_201_CREATED,
    response_description="El log fue registrado y se retorna el id_log generado.",
    responses={
        201: {
            "description": "Log registrado.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "id_log": 99,
                        "usuario_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    }
                }
            },
        },
        422: {
            "description": "El cuerpo de la petición no cumple el esquema.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "pregunta_rag"],
                                "msg": "Field required",
                                "type": "missing",
                            }
                        ]
                    }
                }
            },
        },
        503: {
            "description": "Base de datos no disponible.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "La base de datos no está disponible en este momento."
                    }
                }
            },
        },
    },
)
async def registrar_log_rag(log: LogRagIn):
    try:
        conn = await get_db_connection()
    except Exception as exc:
        if is_db_connection_error(exc):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=DB_UNAVAILABLE_MSG,
            )
        raise_for_unexpected(exc)

    try:
        usuario_uuid = log.usuario_id
        if usuario_uuid is None and log.auth0_id:
            usuario_uuid = await conn.fetchval(
                "SELECT usuario_id FROM usuarios WHERE auth0_id = $1", log.auth0_id
            )
            if usuario_uuid is None:
                usuario_uuid = await conn.fetchval(
                    "INSERT INTO usuarios (auth0_id, email) VALUES ($1, $2) RETURNING usuario_id",
                    log.auth0_id,
                    log.email,
                )

        detalle = log.detalle or f"Consulta RAG: {log.pregunta_rag}"
        id_log = await conn.fetchval(
            """INSERT INTO logs
               (usuario_id, tipo_transaccion, pregunta_rag, respuesta_rag, detalle)
               VALUES ($1, $2, $3, $4, $5)
               RETURNING id_log""",
            usuario_uuid,
            log.tipo_transaccion,
            log.pregunta_rag,
            log.respuesta_rag,
            detalle,
        )
        return {
            "status": "success",
            "id_log": id_log,
            "usuario_id": str(usuario_uuid) if usuario_uuid else None,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise_for_unexpected(exc)
    finally:
        await conn.close()
