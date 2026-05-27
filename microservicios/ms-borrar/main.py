import os
from fastapi import FastAPI, HTTPException, status, Depends, Path
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
from shared.auth import validar_token_auth0
from shared.errors import raise_for_unexpected, is_db_connection_error, DB_UNAVAILABLE_MSG

# ---------------------------------------------------------------------------
# Configuración de la aplicación
# ---------------------------------------------------------------------------
_TAGS = [
    {
        "name": "Personas",
        "description": "Operaciones de **eliminación definitiva** de registros de personas.",
    },
]

_DESCRIPTION = """
## Microservicio Borrar — ExplorApp

Responsable de **eliminar permanentemente** el registro de una persona de la base de datos.

### Flujo principal
1. El cliente envía `DELETE /api/personas/{documento}` con el JWT en `Authorization: Bearer <token>`.
2. El servicio valida el token, verifica que el registro exista y lo elimina físicamente.
3. Se registra la operación en `logs` antes de confirmar la transacción.

> La eliminación es **física** (no lógica). No hay papelera ni forma de recuperar el registro una vez eliminado.

### Autenticación
Los endpoints protegidos requieren el encabezado:
```
Authorization: Bearer <access_token>
```
El token se obtiene desde Auth0 con el audience `https://api.explorapp`.
"""

app = FastAPI(
    title="MS-Borrar · ExplorApp",
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


@app.delete(
    "/api/personas/{documento}",
    tags=["Personas"],
    summary="Eliminar persona definitivamente",
    description="""
Elimina **de forma permanente** el registro de la persona con el número de documento indicado.

> Esta operación **no se puede deshacer**. El registro es eliminado físicamente de la tabla `personas`.

### Efectos secundarios
- Se inserta una entrada en `logs` con `tipo_transaccion = 'BORRAR'` antes de que la transacción se confirme, garantizando trazabilidad.
- La foto de perfil almacenada en el volumen `/app/uploads` no se elimina automáticamente.
""",
    status_code=status.HTTP_200_OK,
    response_description="La persona fue eliminada exitosamente.",
    responses={
        200: {
            "description": "Eliminación exitosa.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Documento 1003377298 eliminado del sistema",
                    }
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
async def borrar_persona(
    documento: str = Path(
        ...,
        description="Número de documento de la persona a eliminar. Entre 1 y 10 dígitos numéricos.",
        example="1003377298",
        pattern=r"^[0-9]{1,10}$",
    ),
    token_payload: dict = Depends(validar_token_auth0),
):
    auth0_id = token_payload.get("sub")
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

            await conn.execute("DELETE FROM personas WHERE nro_documento = $1", documento)

            usuario_uuid = await conn.fetchval(
                "SELECT usuario_id FROM usuarios WHERE auth0_id = $1", auth0_id
            )
            detalle_log = f"Eliminación definitiva del documento {documento}"

            await conn.execute(
                """INSERT INTO logs (usuario_id, tipo_transaccion, documento_relacionado, detalle)
                   VALUES ($1, $2, $3, $4)""",
                usuario_uuid,
                "BORRAR",
                documento,
                detalle_log,
            )

        return {"status": "success", "message": f"Documento {documento} eliminado del sistema"}

    except HTTPException:
        raise
    except Exception as exc:
        raise_for_unexpected(exc)
    finally:
        await conn.close()
