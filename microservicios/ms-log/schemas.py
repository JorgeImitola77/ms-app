from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class LogRagIn(BaseModel):
    tipo_transaccion: str = "CONSULTA_RAG"
    # auth0_id es el 'sub' del JWT (p.ej. 'auth0|abc'); el servicio lo resuelve a usuario_id (UUID).
    auth0_id: Optional[str] = None
    email: Optional[str] = None
    usuario_id: Optional[UUID] = None
    pregunta_rag: str
    respuesta_rag: str
    detalle: Optional[str] = None

class LogOut(BaseModel):
    id_log: int
    usuario_id: Optional[UUID] = None
    email_usuario: Optional[str] = None
    fecha_transaccion: datetime
    tipo_transaccion: str
    documento_relacionado: Optional[str] = None
    pregunta_rag: Optional[str] = None
    respuesta_rag: Optional[str] = None
    detalle: str