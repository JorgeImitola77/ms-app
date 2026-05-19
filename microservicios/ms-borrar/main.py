import os
from fastapi import FastAPI, HTTPException, status, Depends
import asyncpg
from shared.auth import validar_token_auth0

app = FastAPI(title="Microservicio Borrar (Auth0)")
DATABASE_URL = os.getenv("DATABASE_URL")

async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)

@app.delete("/api/personas/{documento}", status_code=status.HTTP_200_OK)
async def borrar_persona(documento: str, token_payload: dict = Depends(validar_token_auth0)):
    auth0_id = token_payload.get("sub")
    conn = await get_db_connection()
    try:
        async with conn.transaction():
            existe = await conn.fetchval("SELECT 1 FROM personas WHERE nro_documento = $1", documento)
            if not existe:
                raise HTTPException(status_code=404, detail="Persona no encontrada")

            # Borrar registro físico
            await conn.execute("DELETE FROM personas WHERE nro_documento = $1", documento)

            # Registrar acción en los logs
            usuario_uuid = await conn.fetchval("SELECT usuario_id FROM usuarios WHERE auth0_id = $1", auth0_id)
            detalle_log = f"Eliminación definitiva del registro hecha por el operador {auth0_id}"
            
            await conn.execute(
                """INSERT INTO logs (usuario_id, tipo_transaccion, documento_relacionado, detalle) 
                   VALUES ($1, $2, $3, $4)""",
                usuario_uuid, 'BORRAR', documento, detalle_log
            )

        return {"status": "success", "message": f"Documento {documento} eliminado del sistema"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()