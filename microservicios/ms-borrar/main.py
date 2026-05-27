import os
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
from shared.auth import validar_token_auth0
from shared.errors import raise_for_unexpected, is_db_connection_error, DB_UNAVAILABLE_MSG

app = FastAPI(title="Microservicio Borrar (Auth0)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
DATABASE_URL = os.getenv("DATABASE_URL")

async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)

@app.delete("/api/personas/{documento}", status_code=status.HTTP_200_OK)
async def borrar_persona(documento: str, token_payload: dict = Depends(validar_token_auth0)):
    auth0_id = token_payload.get("sub")
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
            existe = await conn.fetchval("SELECT 1 FROM personas WHERE nro_documento = $1", documento)
            if not existe:
                raise HTTPException(status_code=404, detail="Persona no encontrada")

            await conn.execute("DELETE FROM personas WHERE nro_documento = $1", documento)

            usuario_uuid = await conn.fetchval("SELECT usuario_id FROM usuarios WHERE auth0_id = $1", auth0_id)
            detalle_log = f"Eliminación definitiva del documento {documento}"

            await conn.execute(
                """INSERT INTO logs (usuario_id, tipo_transaccion, documento_relacionado, detalle)
                   VALUES ($1, $2, $3, $4)""",
                usuario_uuid, 'BORRAR', documento, detalle_log
            )

        return {"status": "success", "message": f"Documento {documento} eliminado del sistema"}

    except HTTPException:
        raise
    except Exception as exc:
        raise_for_unexpected(exc)
    finally:
        await conn.close()
