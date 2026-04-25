from pydantic import BaseModel
from datetime import date
from typing import Optional

class PersonaOut(BaseModel):
    nro_documento: str
    tipo_documento: str
    primer_nombre: str
    segundo_nombre: Optional[str] = None
    apellidos: str
    fecha_nacimiento: date
    genero: str
    correo: str
    celular: str
    foto_ruta: Optional[str] = None