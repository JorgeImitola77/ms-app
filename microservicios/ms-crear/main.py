import os
from datetime import date
from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, File, Form, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
import asyncpg
from shared.auth import validar_token_auth0
from shared.models import PersonaCreate
from shared.errors import raise_for_unexpected, is_db_connection_error, DB_UNAVAILABLE_MSG

# ---------------------------------------------------------------------------
# Configuración de la aplicación
# ---------------------------------------------------------------------------
_TAGS = [
    {
        "name": "Personas",
        "description": "Operaciones de **creación** de registros de personas en la base de datos.",
    },
    {
        "name": "Utilidades",
        "description": "Endpoints de diagnóstico y monitoreo del microservicio.",
    },
]

_DESCRIPTION = """
## Microservicio Crear — ExplorApp

Responsable de **registrar nuevas personas** en el sistema.

### Flujo principal
1. El cliente envía los datos de la persona como `multipart/form-data` junto con un JWT de Auth0 en la cabecera `Authorization: Bearer <token>`.
2. El servicio valida el token, auto-registra al usuario autenticado si es la primera vez que opera, guarda los datos en la tabla `personas` y escribe una entrada de auditoría en `logs`.
3. La foto es **opcional**; si se envía debe ser una imagen (`image/*`) y no superar **2 MB**.

### Autenticación
Los endpoints protegidos requieren el encabezado:
```
Authorization: Bearer <access_token>
```
El token se obtiene desde Auth0 con el audience `https://api.explorapp`.
"""

app = FastAPI(
    title="MS-Crear · ExplorApp",
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
UPLOAD_DIR = "/app/uploads"
MAX_FOTO_BYTES = 2 * 1024 * 1024

os.makedirs(UPLOAD_DIR, exist_ok=True)


async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}


@app.get(
    "/test-db",
    tags=["Utilidades"],
    summary="Prueba de conexion a PostgreSQL",
    description=(
        "Establece una conexión directa a la base de datos y devuelve la versión "
        "de PostgreSQL. Útil para verificar que el servicio puede alcanzar la BD. "
        "**No requiere autenticación.**"
    ),
    response_description="Estado de la conexión y versión de PostgreSQL.",
    responses={
        200: {
            "description": "Conexión exitosa o fallida.",
            "content": {
                "application/json": {
                    "examples": {
                        "ok": {
                            "summary": "BD disponible",
                            "value": {
                                "status": "ok",
                                "db_version": "PostgreSQL 15.18 on aarch64-unknown-linux-gnu",
                            },
                        },
                        "error": {
                            "summary": "BD no disponible",
                            "value": {"status": "error", "detalle": "connection refused"},
                        },
                    }
                }
            },
        }
    },
)
async def test_db_connection():
    try:
        conn = await get_db_connection()
        version = await conn.fetchval("SELECT version();")
        await conn.close()
        return {"status": "ok", "db_version": version}
    except Exception as e:
        return {"status": "error", "detalle": str(e)}


@app.post(
    "/api/personas",
    tags=["Personas"],
    summary="Registrar nueva persona",
    description="""
Crea un nuevo registro de persona en la base de datos.

**Tipo de contenido:** `multipart/form-data` (obligatorio para poder enviar la foto).

### Campos del formulario

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `nro_documento` | string | Si | 1 a 10 dígitos numéricos |
| `tipo_documento` | string | Si | `"Tarjeta de identidad"` o `"Cédula"` |
| `primer_nombre` | string | Si | Máx. 30 caracteres, sin dígitos |
| `segundo_nombre` | string | No | Máx. 30 caracteres, sin dígitos |
| `apellidos` | string | Si | Máx. 60 caracteres, sin dígitos |
| `fecha_nacimiento` | string | Si | Formato `YYYY-MM-DD` |
| `genero` | string | Si | `"Masculino"`, `"Femenino"`, `"No binario"` o `"Prefiero no reportar"` |
| `correo` | string | Si | Dirección de correo electrónico válida |
| `celular` | string | Si | Exactamente 10 dígitos numéricos |
| `foto` | file | No | Imagen (`image/*`), máx. 2 MB |

### Efectos secundarios
- Si el usuario autenticado no existe en la tabla `usuarios`, se **auto-registra** usando el `sub` y el email del JWT.
- Se inserta una entrada en `logs` con `tipo_transaccion = 'CREAR'`.
""",
    status_code=status.HTTP_201_CREATED,
    response_description="La persona fue registrada exitosamente.",
    responses={
        201: {
            "description": "Persona registrada.",
            "content": {
                "application/json": {
                    "example": {"status": "success", "message": "Persona registrada exitosamente"}
                }
            },
        },
        401: {
            "description": "Token ausente, inválido o expirado.",
            "content": {"application/json": {"example": {"detail": "El token ha expirado"}}},
        },
        409: {
            "description": "El número de documento ya existe en la base de datos.",
            "content": {
                "application/json": {
                    "example": {"detail": "Ya existe una persona con ese documento."}
                }
            },
        },
        422: {
            "description": "Error de validación. Algún campo no cumple las reglas.",
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
async def crear_persona(
    nro_documento: str = Form(..., description="Número de documento: 1 a 10 dígitos numéricos.", example="1003377298"),
    tipo_documento: str = Form(..., description='Tipo de documento. Valores aceptados: `"Tarjeta de identidad"` o `"Cédula"`.', example="Cédula"),
    primer_nombre: str = Form(..., description="Primer nombre. Máx. 30 caracteres, sin números.", example="Zenen"),
    segundo_nombre: str = Form(None, description="Segundo nombre (opcional). Máx. 30 caracteres, sin números.", example="Andrés"),
    apellidos: str = Form(..., description="Apellidos. Máx. 60 caracteres, sin números.", example="Contreras Royero"),
    fecha_nacimiento: str = Form(..., description="Fecha de nacimiento en formato `YYYY-MM-DD`.", example="2000-05-15"),
    genero: str = Form(..., description='Género. Valores: `"Masculino"`, `"Femenino"`, `"No binario"`, `"Prefiero no reportar"`.', example="Masculino"),
    correo: str = Form(..., description="Correo electrónico válido.", example="zenen@ejemplo.com"),
    celular: str = Form(..., description="Número de celular colombiano: exactamente 10 dígitos.", example="3001234567"),
    foto: UploadFile = File(None, description="Foto de perfil. Formatos aceptados: JPEG, PNG, WEBP. Tamaño máximo: 2 MB."),
    token_payload: dict = Depends(validar_token_auth0),
):
    try:
        PersonaCreate(
            tipo_documento=tipo_documento,
            nro_documento=nro_documento,
            primer_nombre=primer_nombre,
            segundo_nombre=segundo_nombre,
            apellidos=apellidos,
            fecha_nacimiento=fecha_nacimiento,
            genero=genero,
            correo=correo,
            celular=celular,
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(),
        )

    file_path = None
    if foto and foto.filename:
        contenido = await foto.read()
        if len(contenido) > MAX_FOTO_BYTES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="La foto no debe superar los 2 MB.",
            )
        if not (foto.content_type or "").startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El archivo enviado no es una imagen válida.",
            )
        extension = foto.filename.split(".")[-1]
        file_path = f"{UPLOAD_DIR}/{nro_documento}.{extension}"
        with open(file_path, "wb") as f:
            f.write(contenido)

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
            auth0_id = token_payload.get("sub")
            email_from_token = token_payload.get("email")

            row = await conn.fetchrow(
                "SELECT usuario_id, email FROM usuarios WHERE auth0_id = $1", auth0_id
            )

            if not row:
                usuario_uuid = await conn.fetchval(
                    "INSERT INTO usuarios (auth0_id, email) VALUES ($1, $2) RETURNING usuario_id",
                    auth0_id,
                    email_from_token,
                )
            else:
                usuario_uuid = row["usuario_id"]
                if email_from_token and not row["email"]:
                    await conn.execute(
                        "UPDATE usuarios SET email = $1 WHERE usuario_id = $2",
                        email_from_token,
                        usuario_uuid,
                    )

            await conn.execute(
                """INSERT INTO personas (nro_documento, tipo_documento, primer_nombre, segundo_nombre,
                apellidos, fecha_nacimiento, genero, correo, celular, foto_ruta, creado_por)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)""",
                nro_documento,
                tipo_documento,
                primer_nombre,
                segundo_nombre,
                apellidos,
                date.fromisoformat(fecha_nacimiento),
                genero,
                correo,
                celular,
                file_path,
                usuario_uuid,
            )

            detalle_log = f"Creación exitosa de {primer_nombre} {apellidos}"
            await conn.execute(
                """INSERT INTO logs (usuario_id, tipo_transaccion, documento_relacionado, detalle)
                   VALUES ($1, $2, $3, $4)""",
                usuario_uuid,
                "CREAR",
                nro_documento,
                detalle_log,
            )

        return {"status": "success", "message": "Persona registrada exitosamente"}

    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una persona con ese documento.",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise_for_unexpected(exc)
    finally:
        await conn.close()
