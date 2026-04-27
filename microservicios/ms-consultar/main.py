import os
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncpg
from schemas import PersonaOut

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

@app.get("/api/personas/{documento}", response_model=PersonaOut, status_code=status.HTTP_200_OK)
async def consultar_persona(documento: str, token_valido: bool = Depends(validar_token)):
    conn = await get_db_connection()
    try:
        # 1. Buscar a la persona
        registro = await conn.fetchrow(
            "SELECT * FROM personas WHERE nro_documento = $1", documento
        )
        
        if not registro:
            raise HTTPException(status_code=404, detail="Persona no encontrada")

        # 2. Registrar la transacción en el Log de forma asíncrona
        detalle_log = f"Consulta de datos del documento {documento}"
        await conn.execute(
            "INSERT INTO logs (tipo_transaccion, documento_relacionado, detalle) VALUES ($1, $2, $3)",
            'CONSULTAR', documento, detalle_log
        )

        return dict(registro)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()