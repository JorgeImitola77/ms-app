import os
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncpg
from schemas import PersonaOut
from shared.auth import validar_token_auth0

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Microservicio Consultar (Auth0)")
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

@app.get("/api/personas/{documento}", response_model=PersonaOut, status_code=status.HTTP_200_OK)
async def consultar_persona(documento: str, token_payload: dict = Depends(validar_token_auth0)):
    auth0_id = token_payload.get("sub")
    conn = await get_db_connection()
    try:
        # 1. Buscar a la persona
        registro = await conn.fetchrow(
            "SELECT * FROM personas WHERE nro_documento = $1", documento
        )
        
        if not registro:
            raise HTTPException(status_code=404, detail="Persona no encontrada")

        # 2. Registrar la consulta en los Logs asociándolo al usuario interno
        usuario_uuid = await conn.fetchval("SELECT usuario_id FROM usuarios WHERE auth0_id = $1", auth0_id)
        detalle_log = f"Consulta de datos del documento {documento} ejecutada por {auth0_id}"
        
        await conn.execute(
            """INSERT INTO logs (usuario_id, tipo_transaccion, documento_relacionado, detalle) 
               VALUES ($1, $2, $3, $4)""",
            usuario_uuid, 'CONSULTAR', documento, detalle_log
        )
        
        return dict(registro)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()