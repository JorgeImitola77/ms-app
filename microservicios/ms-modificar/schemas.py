from pydantic import BaseModel, Field
from typing import Optional

class PersonaUpdate(BaseModel):
    # Definimos los campos como opcionales
    correo: Optional[str] = None
    celular: Optional[str] = Field(None, min_length=10, max_length=10, pattern=r'^\d+$')
