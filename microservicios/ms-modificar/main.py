import os
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncpg
<<<<<<< Updated upstream
from schemas import PersonaUpdate
=======
from shared.models import PersonaUpdate
from shared.auth import validar_token_auth0
>>>>>>> Stashed changes

app = FastAPI(title="Microservicio Modificar (Auth0)")
auth_scheme = HTTPBearer()
DATABASE_URL = os.getenv("DATABASE_URL")

def validar_token(token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    return True # Simulación para desarrollo

async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)

@app.patch("/api/personas/{documento}", status_code=status.HTTP_200_OK)
<<<<<<< Updated upstream
async def modificar_persona(documento: str, datos: PersonaUpdate, token_valido: bool = Depends(validar_token)):
=======
async def modificar_persona(documento: str, datos: PersonaUpdate, token_payload: dict = Depends(validar_token_auth0)):
    auth0_id = token_payload.get("sub")
    campos_a_actualizar = {k: v for k, v in datos.model_dump(exclude_unset=True).items() if v is not None}
    
    if not campos_a_actualizar:
        raise HTTPException(status_code=400, detail="No se enviaron datos para actualizar")

>>>>>>> Stashed changes
    conn = await get_db_connection()
    try:
        # Extraer solo los datos que no sean nulos
        campos_a_actualizar = {k: v for k, v in datos.dict().items() if v is not None}
        
        if not campos_a_actualizar:
            raise HTTPException(status_code=400, detail="No se enviaron datos para actualizar")

        async with conn.transaction():
            # Verificar si existe
            existe = await conn.fetchval("SELECT 1 FROM personas WHERE nro_documento = $1", documento)
            if not existe:
                raise HTTPException(status_code=404, detail="Persona no encontrada")

            # Construir la consulta SQL dinámica
            set_clauses = []
            valores = []
            for i, (columna, valor) in enumerate(campos_a_actualizar.items(), start=1):
                set_clauses.append(f"{columna} = ${i}")
                valores.append(valor)
            
            valores.append(documento) # El último parámetro es el documento para el WHERE
            query = f"UPDATE personas SET {', '.join(set_clauses)} WHERE nro_documento = ${len(valores)}"
            
            await conn.execute(query, *valores)

<<<<<<< Updated upstream
            # Registrar en el Log
            detalle_log = f"Actualización de datos: {list(campos_a_actualizar.keys())}"
            await conn.execute(
                "INSERT INTO logs (tipo_transaccion, documento_relacionado, detalle) VALUES ($1, $2, $3)",
=======
            # Registrar en logs con el usuario de Auth0
            detalle_log = f"Modificación parcial realizada por {auth0_id}. Campos actualizados: {list(campos_a_actualizar.keys())}"
            
            await conn.execute(
                """INSERT INTO logs (tipo_transaccion, documento_relacionado, detalle) 
                   VALUES ($1, $2, $3)""",
>>>>>>> Stashed changes
                'ACTUALIZAR', documento, detalle_log
            )

        return {"status": "success", "message": "Datos actualizados correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()