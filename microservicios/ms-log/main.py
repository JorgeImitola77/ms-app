import os
from fastapi import FastAPI, HTTPException, status, Depends
from typing import List, Optional
import asyncpg
from schemas import LogOut
from shared.auth import validar_token_auth0

app = FastAPI(title="Microservicio Logs (Auth0)")
DATABASE_URL = os.getenv("DATABASE_URL")

async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)

@app.get("/api/logs", response_model=List[LogEntry], status_code=status.HTTP_200_OK)
async def consultar_logs(
    tipo: Optional[str] = None,
    documento: Optional[str] = None,
    fecha: Optional[str] = None, 
    token_payload: dict = Depends(validar_token_auth0) # Validando acceso real a auditoría
):
    conn = await get_db_connection()
    try:
        query = "SELECT * FROM logs WHERE 1=1"
        valores = []
        contador = 1

        if tipo:
            query += f" AND tipo_transaccion = ${contador}"
            valores.append(tipo)
            contador += 1
            
        if documento:
            query += f" AND documento_relacionado = ${contador}"
            valores.append(documento)
            contador += 1
            
        if fecha:
            query += f" AND DATE(fecha_transaccion) = ${contador}"
            valores.append(fecha)
            contador += 1

        query += " ORDER BY fecha_transaccion DESC"
        registros = await conn.fetch(query, *valores)
        
        # Mapea dinámicamente las filas incluyendo los campos RAG si vienen en la base de datos
        return [dict(reg) for reg in registros]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()