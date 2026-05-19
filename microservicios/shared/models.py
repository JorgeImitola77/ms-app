from pydantic import BaseModel, Field, EmailStr
from typing import Literal, Optional
from datetime import date, datetime

# ==========================================
# MODELOS DE PERSONA
# ==========================================
class PersonaCreate(BaseModel):
    tipo_documento: Literal['Tarjeta de identidad', 'Cédula']
    nro_documento: str = Field(pattern=r'^[0-9]{1,10}$')
    primer_nombre: str = Field(max_length=30, pattern=r'^[^0-9]+$')
    segundo_nombre: Optional[str] = Field(default=None, max_length=30, pattern=r'^[^0-9]+$')
    apellidos: str = Field(max_length=60, pattern=r'^[^0-9]+$')
    fecha_nacimiento: date
    # Nota: Puse 'Femenino' con mayúscula para que coincida exactamente con tu init.sql
    genero: Literal['Masculino', 'Femenino', 'No binario', 'Prefiero no reportar']
    correo: EmailStr
    celular: str = Field(pattern=r'^[0-9]{10}$')

class PersonaUpdate(BaseModel):
    tipo_documento: Optional[Literal['Tarjeta de identidad', 'Cédula']] = None
    nro_documento: Optional[str] = Field(default=None, pattern=r'^[0-9]{1,10}$')
    primer_nombre: Optional[str] = Field(default=None, max_length=30, pattern=r'^[^0-9]+$')
    segundo_nombre: Optional[str] = Field(default=None, max_length=30, pattern=r'^[^0-9]+$')
    apellidos: Optional[str] = Field(default=None, max_length=60, pattern=r'^[^0-9]+$')
    fecha_nacimiento: Optional[date] = None
    genero: Optional[Literal['Masculino', 'Femenino', 'No binario', 'Prefiero no reportar']] = None
    correo: Optional[EmailStr] = None
    celular: Optional[str] = Field(default=None, pattern=r'^[0-9]{10}$')

class PersonaResponse(PersonaCreate):
    foto_ruta: Optional[str] = None
    fecha_registro: datetime

# ==========================================
# MODELOS DE LOGS
# ==========================================
class LogEntry(BaseModel):
    id_log: int
    fecha_transaccion: datetime
    tipo_transaccion: str
    documento_relacionado: Optional[str] = None
    detalle: str

class LogQuery(BaseModel):
    tipo_transaccion: Optional[str] = None
    documento_relacionado: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None