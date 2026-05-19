import os
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
import asyncpg
from shared.models import LogEntry
from shared.auth import validar_token_auth0

app = FastAPI(title="Microservicio Logs (Auth0)")
auth_scheme = HTTPBearer()
DATABASE_URL = os.getenv("DATABASE_URL")

# --- SEGURIDAD ---
def validar_token(token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    return True # Simulación para desarrollo

# --- CONEXIÓN DB ---
async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)

@app.get("/api/logs", response_model=List[LogEntry], status_code=status.HTTP_200_OK)
async def consultar_logs(
    tipo: Optional[str] = None,
    documento: Optional[str] = None,
    fecha: Optional[str] = None, 
    token_payload: dict = Depends(validar_token_auth0)
):
    conn = await get_db_connection()
    try:
        query = "SELECT id_log, fecha_transaccion, tipo_transaccion, documento_relacionado, detalle FROM logs WHERE 1=1"
        valores = []
        contador = 1

        # Si mandan el filtro de 'tipo', lo agregamos a la consulta
        if tipo:
            query += f" AND tipo_transaccion = ${contador}"
            valores.append(tipo)
            contador += 1
            
        # Si mandan el filtro de 'documento', lo agregamos
        if documento:
            query += f" AND documento_relacionado = ${contador}"
            valores.append(documento)
            contador += 1
            
        # Si mandan fecha, casteamos la fecha de transacción para ignorar la hora en la búsqueda
        if fecha:
            query += f" AND DATE(fecha_transaccion) = ${contador}"
            valores.append(fecha)
            contador += 1

        # Ordenar siempre del más reciente al más antiguo
        query += " ORDER BY fecha_transaccion DESC"

        # Ejecutar la consulta en PostgreSQL
        registros = await conn.fetch(query, *valores)
        
        return [dict(r) for r in registros]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()