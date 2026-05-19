from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LogOut(BaseModel):
    id_log: int
    usuario_id: Optional[str] = None
    fecha_transaccion: datetime
    tipo_transaccion: str
    documento_relacionado: Optional[str] = None
    pregunta_rag: Optional[str] = None
    respuesta_rag: Optional[str] = None
    detalle: str