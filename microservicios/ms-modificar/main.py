import os
from fastapi import FastAPI, HTTPException, status, Depends, Path
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
from shared.models import PersonaUpdate
from shared.auth import validar_token_auth0
from shared.errors import raise_for_unexpected, is_db_connection_error, DB_UNAVAILABLE_MSG

# ---------------------------------------------------------------------------
# Configuración de la aplicación
# ---------------------------------------------------------------------------
_TAGS = [
    {
        "name": "Personas",
        "description": "Operaciones de **modificación parcial** de registros de personas.",
    },
]

_DESCRIPTION = """
## Microservicio Modificar — ExplorApp

Responsable de **actualizar parcialmente** los datos de una persona existente.

### Flujo principal
1. El cliente envía `PATCH /api/personas/{documento}` con un JSON que contiene **solo los campos a modificar** y el JWT en `Authorization: Bearer <token>`.
2. El servicio construye dinámicamente la sentencia `UPDATE` con los campos presentes en el cuerpo.
3. Se registra la operación en `logs` indicando qué campos fueron modificados.

> El `nro_documento` (clave primaria) **no puede modificarse** a través de este endpoint.

### Autenticación
Los endpoints protegidos requieren el encabezado:
```
Authorization: Bearer <access_token>
```
El token se obtiene desde Auth0 con el audience `https://api.explorapp`.
"""

app = FastAPI(
    title="MS-Modificar · ExplorApp",
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


@app.patch(
    "/api/personas/{documento}",
    tags=["Personas"],
    summary="Actualizar datos de una persona (parcial)",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "solo_correo": {
                            "summary": "Actualizar solo el correo",
                            "value": {"correo": "nuevo@correo.com"},
                        },
                        "varios_campos": {
                            "summary": "Actualizar nombre y celular",
                            "value": {"primer_nombre": "Zenen", "celular": "3109876543"},
                        },
                    }
                }
            }
        }
    },
    description="""
Actualiza **uno o más campos** de la persona identificada por `documento`.

### Cuerpo de la petición (JSON)
Envía únicamente los campos que deseas cambiar. Todos son opcionales.

```json
{
  "primer_nombre": "Zenen",
  "correo": "nuevo@correo.com"
}
```

### Campos modificables

| Campo | Tipo | Restricciones |
|---|---|---|
| `tipo_documento` | string | `"Tarjeta de identidad"` o `"Cédula"` |
| `primer_nombre` | string | Máx. 30 caracteres, sin dígitos |
| `segundo_nombre` | string | Máx. 30 caracteres, sin dígitos |
| `apellidos` | string | Máx. 60 caracteres, sin dígitos |
| `fecha_nacimiento` | date | Formato `YYYY-MM-DD` |
| `genero` | string | `"Masculino"`, `"Femenino"`, `"No binario"`, `"Prefiero no reportar"` |
| `correo` | string | Email válido |
| `celular` | string | Exactamente 10 dígitos |

> El `nro_documento` **no** puede cambiarse (es la clave primaria del registro).

### Efectos secundarios
- Se inserta una entrada en `logs` con `tipo_transaccion = 'MODIFICAR'` y la lista de campos actualizados.
""",
    status_code=status.HTTP_200_OK,
    response_description="La persona fue actualizada exitosamente.",
    responses={
        200: {
            "description": "Actualización exitosa.",
            "content": {
                "application/json": {
                    "example": {"status": "success", "message": "Datos actualizados correctamente"}
                }
            },
        },
        400: {
            "description": "El cuerpo de la petición no contiene ningún campo para actualizar.",
            "content": {
                "application/json": {
                    "example": {"detail": "No se enviaron datos para actualizar"}
                }
            },
        },
        401: {
            "description": "Token ausente, inválido o expirado.",
            "content": {"application/json": {"example": {"detail": "El token ha expirado"}}},
        },
        404: {
            "description": "No existe una persona con ese número de documento.",
            "content": {
                "application/json": {"example": {"detail": "Persona no encontrada"}}
            },
        },
        422: {
            "description": "Error de validación en alguno de los campos enviados.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "celular"],
                                "msg": "String should match pattern '^[0-9]{10}$'",
                                "type": "string_pattern_mismatch",
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
async def modificar_persona(
    documento: str = Path(
        ...,
        description="Número de documento de la persona a modificar. Entre 1 y 10 dígitos numéricos.",
        example="1003377298",
        pattern=r"^[0-9]{1,10}$",
    ),
    datos: PersonaUpdate = ...,
    token_payload: dict = Depends(validar_token_auth0),
):
    auth0_id = token_payload.get("sub")
    campos_a_actualizar = {
        k: v for k, v in datos.model_dump(exclude_unset=True).items() if v is not None
    }

    if not campos_a_actualizar:
        raise HTTPException(status_code=400, detail="No se enviaron datos para actualizar")

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
        async with conn.transaction():
            existe = await conn.fetchval(
                "SELECT 1 FROM personas WHERE nro_documento = $1", documento
            )
            if not existe:
                raise HTTPException(status_code=404, detail="Persona no encontrada")

            set_clauses = [f"{k} = ${i+1}" for i, k in enumerate(campos_a_actualizar.keys())]
            query = (
                f"UPDATE personas SET {', '.join(set_clauses)} "
                f"WHERE nro_documento = ${len(campos_a_actualizar)+1}"
            )

            valores = list(campos_a_actualizar.values())
            valores.append(documento)

            await conn.execute(query, *valores)

            usuario_uuid = await conn.fetchval(
                "SELECT usuario_id FROM usuarios WHERE auth0_id = $1", auth0_id
            )
            detalle_log = (
                f"Modificación parcial. Campos actualizados: {list(campos_a_actualizar.keys())}"
            )

            await conn.execute(
                "INSERT INTO logs (usuario_id, tipo_transaccion, documento_relacionado, detalle) "
                "VALUES ($1, $2, $3, $4)",
                usuario_uuid,
                "MODIFICAR",
                documento,
                detalle_log,
            )

        return {"status": "success", "message": "Datos actualizados correctamente"}

    except HTTPException:
        raise
    except Exception as exc:
        raise_for_unexpected(exc)
    finally:
        await conn.close()
