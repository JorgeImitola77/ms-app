import os
from datetime import date
from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncpg
from shared.auth import validar_token_auth0
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from shared.database import get_db

app = FastAPI(title="Microservicio Crear (Auth0)")
auth_scheme = HTTPBearer()

# CONFIGURACIÓN AUTH0 (Reemplazar con tus datos de Auth0)
AUTH0_DOMAIN = "tu-dominio.auth0.com"
ALGORITHMS = ["RS256"]
DATABASE_URL = os.getenv("DATABASE_URL")
UPLOAD_DIR = "/app/uploads" # Carpeta dentro del contenedor

# Asegurar que la carpeta de fotos existe
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- SEGURIDAD ---
def validar_token(token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    """Valida el token JWT enviado desde el aplicativo Android."""
    try:
        # En producción, aquí se descarga la llave pública de Auth0 para verificar la firma
        # payload = jwt.decode(token.credentials, key_publica, algorithms=ALGORITHMS)
        # return payload
        return True # Simulación de validación exitosa para desarrollo
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

# --- LÓGICA DE BASE DE DATOS ---
async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)

@app.get("/test-db")
async def test_db_connection(db: AsyncSession = Depends(get_db)):
    """Endpoint para probar la conexión a PostgreSQL con asyncpg"""
    try:
        result = await db.execute(text("SELECT version();"))
        version = result.scalar()
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
    foto: UploadFile = File(...),
    token_payload: dict = Depends(validar_token_auth0)
):
    auth0_id = token_payload.get("sub")

    # 1. VALIDAR TAMAÑO DE LA FOTO
    contenido = await foto.read()
    if len(contenido) > MAX_FILE_SIZE:
        raise HTTPException(status_code=422, detail="La foto supera el límite de 2MB")
    
    # 2. GUARDAR ARCHIVO FÍSICO
    file_extension = foto.filename.split(".")[-1]
    file_path = f"{UPLOAD_DIR}/{nro_documento}.{file_extension}"
    with open(file_path, "wb") as f:
        f.write(contenido)

    # 3. GUARDAR EN BASE DE DATOS Y LOGS
    conn = await get_db_connection()
    try:
        async with conn.transaction():
            # Insertar Persona asociando las columnas correctas de init.sql
            await conn.execute(
                """INSERT INTO personas (nro_documento, tipo_documento, primer_nombre, segundo_nombre, 
                apellidos, fecha_nacimiento, genero, correo, celular, foto_ruta) 
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)""",
                nro_documento, tipo_documento, primer_nombre, segundo_nombre, 
                apellidos, date.fromisoformat(fecha_nacimiento), genero, correo, celular, file_path
            )
            
            # Insertar Log de auditoría según la estructura de init.sql
            detalle_log = f"Creación exitosa de {primer_nombre} {apellidos} por usuario {auth0_id}"
            await conn.execute(
                """INSERT INTO logs (tipo_transaccion, documento_relacionado, detalle) 
                   VALUES ($1, $2, $3)""",
                'CREAR', nro_documento, detalle_log
            )

        return {"status": "success", "message": "Persona registrada en ExplorApp"}
    
    except Exception as e:
        if os.path.exists(file_path): os.remove(file_path) # Borrar foto si falla la DB
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await conn.close()