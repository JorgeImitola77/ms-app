import os
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncpg

app = FastAPI(title="Microservicio Borrar (Auth0)")
auth_scheme = HTTPBearer()
DATABASE_URL = os.getenv("DATABASE_URL")

def validar_token(token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    return True # Simulación para desarrollo

async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)

@app.delete("/api/personas/{documento}", status_code=status.HTTP_200_OK)
async def borrar_persona(documento: str, token_valido: bool = Depends(validar_token)):
    conn = await get_db_connection()
    try:
        async with conn.transaction():
            # 1. Verificar si existe la persona
            existe = await conn.fetchval("SELECT 1 FROM personas WHERE nro_documento = $1", documento)
            if not existe:
                raise HTTPException(status_code=404, detail="Persona no encontrada")

            # 2. Borrar el registro
            await conn.execute("DELETE FROM personas WHERE nro_documento = $1", documento)

            # Registrar acción en los logs
            detalle_log = f"Eliminación definitiva del registro hecha por el operador {auth0_id}"
            
            await conn.execute(
                """INSERT INTO logs (tipo_transaccion, documento_relacionado, detalle) \
                   VALUES ($1, $2, $3)""",
                'BORRAR', documento, detalle_log
            )

        return {"status": "success", "message": f"Documento {documento} eliminado del sistema"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()