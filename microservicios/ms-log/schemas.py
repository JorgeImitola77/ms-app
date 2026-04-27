from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LogOut(BaseModel):
    id_log: int
    fecha_transaccion: datetime
    tipo_transaccion: str
    documento_relacionado: Optional[str] = None
    detalle: str