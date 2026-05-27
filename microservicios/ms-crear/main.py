import os
from datetime import date
from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
from shared.auth import validar_token_auth0

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
    # Guardar la foto si se proporcionó
    file_path = None
    if foto and foto.filename:
        contenido = await foto.read()
        if len(contenido) > 2 * 1024 * 1024:
            raise HTTPException(status_code=422, detail="La foto no debe superar los 2 MB")
        extension = foto.filename.split('.')[-1]
        file_path = f"{UPLOAD_DIR}/{nro_documento}.{extension}"
        with open(file_path, "wb") as f:
            f.write(contenido)

    conn = await get_db_connection()
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
        # 409 Conflict es el código REST correcto para recursos duplicados.
        raise HTTPException(status_code=409, detail="El número de documento ya se encuentra registrado")
    except HTTPException:
        # Validaciones internas (p. ej. foto > 2MB) deben mantener su status.
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()