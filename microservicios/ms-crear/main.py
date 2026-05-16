import os
import shutil
from datetime import date
from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, File, Form
import asyncpg
from shared.auth import validar_token_auth0

app = FastAPI(title="Microservicio Crear (Auth0)")
DATABASE_URL = os.getenv("DATABASE_URL")
UPLOAD_DIR = "/app/uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)

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
    foto: UploadFile = File(...),
    token_payload: dict = Depends(validar_token_auth0) # Dependencia real aplicada
):
    # Extraer el auth0_id único del usuario autenticado
    auth0_id = token_payload.get("sub")

    # 1. VALIDAR TAMAÑO DE LA FOTO
    contenido = await foto.read()
    if len(contenido) > 2 * 1024 * 1024:
        raise HTTPException(status_code=422, detail="La foto no debe superar los 2 MB")

    # 2. GUARDAR FOTO FÍSICA
    file_extension = foto.filename.split(".")[-1]
    file_path = f"{UPLOAD_DIR}/{nro_documento}.{file_extension}"
    with open(file_path, "wb") as f:
        f.write(contenido)

    conn = await get_db_connection()
    try:
        async with conn.transaction():
            # Obtener el usuario_id (UUID) interno correspondiente al auth0_id para respetar la FK
            usuario_uuid = await conn.fetchval(
                "SELECT usuario_id FROM usuarios WHERE auth0_id = $1", auth0_id
            )
            
            # Si el usuario no existe en nuestra tabla interna, lo registramos dinámicamente con los claims básicos
            if not usuario_uuid:
                usuario_uuid = await conn.fetchval(
                    """INSERT INTO usuarios (auth0_id, email) 
                       VALUES ($1, $2) RETURNING usuario_id""",
                    auth0_id, token_payload.get("email")
                )

            # Insertar Persona asociando el UUID obtenido
            await conn.execute(
                """INSERT INTO personas (nro_documento, tipo_documento, primer_nombre, segundo_nombre, 
                apellidos, fecha_nacimiento, genero, correo, celular, foto_ruta) 
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)""",
                nro_documento, tipo_documento, primer_nombre, segundo_nombre, 
                apellidos, date.fromisoformat(fecha_nacimiento), genero, correo, celular, file_path, usuario_uuid
            )
            
            # Insertar Log de auditoría con las relaciones
            detalle_log = f"Creación exitosa de {primer_nombre} {apellidos} por usuario {auth0_id}"
            await conn.execute(
                """INSERT INTO logs (usuario_id, tipo_transaccion, documento_relacionado, detalle) 
                   VALUES ($1, $2, $3, $4)""",
                usuario_uuid, 'CREAR', nro_documento, detalle_log
            )

        return {"status": "success", "message": "Persona registrada exitosamente"}
        
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=400, detail="El número de documento ya se encuentra registrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()