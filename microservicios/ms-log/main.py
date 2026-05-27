import os
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import asyncpg
from schemas import LogOut, LogRagIn
from shared.auth import validar_token_auth0
from shared.errors import raise_for_unexpected, is_db_connection_error, DB_UNAVAILABLE_MSG
from datetime import date

app = FastAPI(title="Microservicio Logs (Auth0)")
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

@app.get("/api/logs", response_model=List[LogOut], status_code=status.HTTP_200_OK)
async def consultar_logs(
    tipo: Optional[str] = None,
    documento: Optional[str] = None,
    fecha: Optional[str] = None,
    token_payload: dict = Depends(validar_token_auth0)
):
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
        query = """
            SELECT l.*, u.email AS email_usuario
            FROM logs l
            LEFT JOIN usuarios u ON l.usuario_id = u.usuario_id
            WHERE 1=1"""
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
            try:
                fecha_obj = date.fromisoformat(fecha)
                valores.append(fecha_obj)
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usa YYYY-MM-DD.")
            contador += 1

        query += " ORDER BY fecha_transaccion DESC"
        registros = await conn.fetch(query, *valores)

        return [dict(r) for r in registros]

    except HTTPException:
        raise
    except Exception as exc:
        raise_for_unexpected(exc)
    finally:
        await conn.close()


@app.post("/api/logs/internal", status_code=status.HTTP_201_CREATED)
async def registrar_log_rag(log: LogRagIn):
    """
    Endpoint interno (red privada app_network) usado por el workflow RAG de n8n.
    No exige JWT porque n8n no porta token de usuario; el identificador del usuario
    llega en el body como `auth0_id` (sub del JWT) y se resuelve al UUID local.
    Registra la transacción CONSULTA_RAG con su pregunta y respuesta.
    """
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
        usuario_uuid = log.usuario_id
        if usuario_uuid is None and log.auth0_id:
            usuario_uuid = await conn.fetchval(
                "SELECT usuario_id FROM usuarios WHERE auth0_id = $1", log.auth0_id
            )
            if usuario_uuid is None:
                usuario_uuid = await conn.fetchval(
                    "INSERT INTO usuarios (auth0_id, email) VALUES ($1, $2) RETURNING usuario_id",
                    log.auth0_id, log.email,
                )

        detalle = log.detalle or f"Consulta RAG: {log.pregunta_rag}"
        id_log = await conn.fetchval(
            """INSERT INTO logs
               (usuario_id, tipo_transaccion, pregunta_rag, respuesta_rag, detalle)
               VALUES ($1, $2, $3, $4, $5)
               RETURNING id_log""",
            usuario_uuid, log.tipo_transaccion, log.pregunta_rag, log.respuesta_rag, detalle
        )
        return {"status": "success", "id_log": id_log, "usuario_id": str(usuario_uuid) if usuario_uuid else None}
    except HTTPException:
        raise
    except Exception as exc:
        raise_for_unexpected(exc)
    finally:
        await conn.close()
