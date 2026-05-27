import os
from datetime import date
from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
import asyncpg
from shared.auth import validar_token_auth0
from shared.models import PersonaCreate
from shared.errors import raise_for_unexpected, is_db_connection_error, DB_UNAVAILABLE_MSG

app = FastAPI(title="Microservicio Crear (Auth0)")
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

@app.get("/test-db")
async def test_db_connection():
    """Endpoint para probar la conexión a PostgreSQL con asyncpg"""
    try:
        conn = await get_db_connection()
        version = await conn.fetchval("SELECT version();")
        await conn.close()
        return {"status": "ok", "db_version": version}
    except Exception as e:
        return {"status": "error", "detalle": str(e)}

@app.post("/api/personas", status_code=status.HTTP_201_CREATED)
async def crear_persona(
    nro_documento: str = Form(...),
    tipo_documento: str = Form(...),
    primer_nombre: str = Form(...),
    segundo_nombre: str = Form(None),
    apellidos: str = Form(...),
    fecha_nacimiento: str = Form(...),
    genero: str = Form(...),
    correo: str = Form(...),
    celular: str = Form(...),
    foto: UploadFile = File(None),
    token_payload: dict = Depends(validar_token_auth0)
):
    # Validar los campos con el mismo esquema Pydantic compartido.
    # Como el endpoint usa multipart/form-data (por la foto) no podemos
    # depender de la validación automática de FastAPI sobre un modelo
    # Pydantic; lanzamos la validación manualmente y devolvemos 422 con
    # el mismo formato que produciría FastAPI.
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

    # Guardar la foto si se proporcionó
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
        extension = foto.filename.split('.')[-1]
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

            # Verificar si el usuario existe en la tabla usuarios
            row = await conn.fetchrow("SELECT usuario_id, email FROM usuarios WHERE auth0_id = $1", auth0_id)

            if not row:
                # Auto-registrarlo si no existe
                usuario_uuid = await conn.fetchval(
                    "INSERT INTO usuarios (auth0_id, email) VALUES ($1, $2) RETURNING usuario_id",
                    auth0_id, email_from_token
                )
            else:
                usuario_uuid = row["usuario_id"]
                # Actualizar email si antes quedó NULL
                if email_from_token and not row["email"]:
                    await conn.execute(
                        "UPDATE usuarios SET email = $1 WHERE usuario_id = $2",
                        email_from_token, usuario_uuid
                    )

            # Insertar Persona asociando el UUID obtenido
            await conn.execute(
                """INSERT INTO personas (nro_documento, tipo_documento, primer_nombre, segundo_nombre,
                apellidos, fecha_nacimiento, genero, correo, celular, foto_ruta, creado_por)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)""",
                nro_documento, tipo_documento, primer_nombre, segundo_nombre,
                apellidos, date.fromisoformat(fecha_nacimiento), genero, correo, celular, file_path, usuario_uuid
            )

            # Insertar Log de auditoría
            detalle_log = f"Creación exitosa de {primer_nombre} {apellidos}"
            await conn.execute(
                """INSERT INTO logs (usuario_id, tipo_transaccion, documento_relacionado, detalle)
                   VALUES ($1, $2, $3, $4)""",
                usuario_uuid, 'CREAR', nro_documento, detalle_log
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
