import os
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncpg
from shared.models import PersonaResponse
from shared.auth import validar_token_auth0

app = FastAPI(title="Microservicio Consultar (Auth0)")
auth_scheme = HTTPBearer()

DATABASE_URL = os.getenv("DATABASE_URL")

# --- SEGURIDAD ---
def validar_token(token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    # Simulación de validación para desarrollo
    return True 

# --- CONEXIÓN DB ---
async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)

@app.get("/api/personas/{documento}", response_model=PersonaResponse, status_code=status.HTTP_200_OK)
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

        # 2. Registrar la consulta en los Logs de auditoría
        detalle_log = f"Consulta de datos del documento {documento} ejecutada por {auth0_id}"
        
        await conn.execute(
            """INSERT INTO logs (tipo_transaccion, documento_relacionado, detalle) 
               VALUES ($1, $2, $3)""",

            'CONSULTAR', documento, detalle_log
        )

        return dict(registro)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()