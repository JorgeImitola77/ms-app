import os
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
from shared.models import PersonaUpdate
from shared.auth import validar_token_auth0

app = FastAPI(title="Microservicio Modificar (Auth0)")
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

@app.patch("/api/personas/{documento}", status_code=status.HTTP_200_OK)
async def modificar_persona(documento: str, datos: PersonaUpdate, token_payload: dict = Depends(validar_token_auth0)):
    auth0_id = token_payload.get("sub")
    campos_a_actualizar = {k: v for k, v in datos.model_dump(exclude_unset=True).items() if v is not None}
    
    if not campos_a_actualizar:
        raise HTTPException(status_code=400, detail="No se enviaron datos para actualizar")

    conn = await get_db_connection()
    try:
        async with conn.transaction():
            existe = await conn.fetchval("SELECT 1 FROM personas WHERE nro_documento = $1", documento)
            if not existe:
                raise HTTPException(status_code=404, detail="Persona no encontrada")

            # Consulta dinámica para la actualización parcial
            set_clauses = [f"{k} = ${i+1}" for i, k in enumerate(campos_a_actualizar.keys())]
            query = f"UPDATE personas SET {', '.join(set_clauses)} WHERE nro_documento = ${len(campos_a_actualizar)+1}"
            
            valores = list(campos_a_actualizar.values())
            valores.append(documento)
            
            await conn.execute(query, *valores)

            # Registrar en logs con el usuario de Auth0
            usuario_uuid = await conn.fetchval("SELECT usuario_id FROM usuarios WHERE auth0_id = $1", auth0_id)
            detalle_log = f"Modificación parcial realizada por {auth0_id}. Campos actualizados: {list(campos_a_actualizar.keys())}"

            await conn.execute(
                "INSERT INTO logs (usuario_id, tipo_transaccion, documento_relacionado, detalle) VALUES ($1, $2, $3, $4)",
                usuario_uuid, 'MODIFICAR', documento, detalle_log
            )

        return {"status": "success", "message": "Datos actualizados correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()