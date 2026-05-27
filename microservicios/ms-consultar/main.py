import os
from fastapi import FastAPI, HTTPException, status, Depends, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncpg
from schemas import PersonaOut
from shared.auth import validar_token_auth0
from shared.errors import raise_for_unexpected, is_db_connection_error, DB_UNAVAILABLE_MSG

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Configuración de la aplicación
# ---------------------------------------------------------------------------
_TAGS = [
    {
        "name": "Personas",
        "description": "Operaciones de **consulta** de registros de personas por número de documento.",
    },
    {
        "name": "Recursos estaticos",
        "description": (
            "Archivos de fotos de perfil servidos directamente desde el volumen compartido. "
            "No requieren autenticación.\n\n"
            "**Base URL:** `http://localhost:8003/uploads/{nombre_archivo}`"
        ),
    },
]

_DESCRIPTION = """
## Microservicio Consultar — ExplorApp

Responsable de **buscar y devolver los datos** de una persona a partir de su número de documento.

### Flujo principal
1. El cliente envía `GET /api/personas/{documento}` con el JWT en `Authorization: Bearer <token>`.
2. El servicio valida el token, busca el registro en la tabla `personas` y registra la operación en `logs`.
3. Si la persona tiene foto, el campo `foto_ruta` apunta al volumen `/app/uploads`. Las imágenes se sirven directamente en `/uploads/{archivo}`.

### Autenticación
Los endpoints protegidos requieren el encabezado:
```
Authorization: Bearer <access_token>
```
El token se obtiene desde Auth0 con el audience `https://api.explorapp`.
"""

app = FastAPI(
    title="MS-Consultar · ExplorApp",
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

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

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
    "/api/personas/{documento}",
    tags=["Personas"],
    summary="Consultar persona por documento",
    description="""
Retorna todos los datos de la persona cuyo `nro_documento` coincida con el parámetro de ruta.

### Respuesta
El cuerpo incluye todos los campos de la tabla `personas`.
Si la persona tiene foto registrada, el campo `foto_ruta` contendrá la ruta interna del servidor
(`/app/uploads/{nro_documento}.{ext}`). Para obtener la imagen directamente usa:

```
GET http://localhost:8003/uploads/{nro_documento}.{ext}
```

### Efectos secundarios
- Se inserta una entrada en `logs` con `tipo_transaccion = 'CONSULTAR'`.
""",
    response_model=PersonaOut,
    status_code=status.HTTP_200_OK,
    response_description="Datos completos de la persona encontrada.",
    responses={
        200: {
            "description": "Persona encontrada.",
            "content": {
                "application/json": {
                    "example": {
                        "nro_documento": "1003377298",
                        "tipo_documento": "Cédula",
                        "primer_nombre": "Zenen",
                        "segundo_nombre": "Andrés",
                        "apellidos": "Contreras Royero",
                        "fecha_nacimiento": "2000-05-15",
                        "genero": "Masculino",
                        "correo": "zenen@ejemplo.com",
                        "celular": "3001234567",
                        "foto_ruta": "/app/uploads/1003377298.jpg",
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
async def consultar_persona(
    documento: str = Path(
        ...,
        description="Número de documento de la persona a consultar. Entre 1 y 10 dígitos numéricos.",
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
        registro = await conn.fetchrow(
            "SELECT * FROM personas WHERE nro_documento = $1", documento
        )

        if not registro:
            raise HTTPException(status_code=404, detail="Persona no encontrada")

        usuario_uuid = await conn.fetchval(
            "SELECT usuario_id FROM usuarios WHERE auth0_id = $1", auth0_id
        )
        detalle_log = f"Consulta de datos del documento {documento}"

        await conn.execute(
            """INSERT INTO logs (usuario_id, tipo_transaccion, documento_relacionado, detalle)
               VALUES ($1, $2, $3, $4)""",
            usuario_uuid,
            "CONSULTAR",
            documento,
            detalle_log,
        )

        return dict(registro)

    except HTTPException:
        raise
    except Exception as exc:
        raise_for_unexpected(exc)
    finally:
        await conn.close()
