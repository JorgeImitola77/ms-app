from pydantic import BaseModel, Field, EmailStr, validator
from datetime import date

class PersonaCreate(BaseModel):
    nro_documento: str = Field(..., max_length=10, pattern=r'^\d+$', description="Máximo 10 caracteres numéricos")
    tipo_documento: str = Field(..., description="Tarjeta de identidad o Cédula")
    primer_nombre: str = Field(..., max_length=30, pattern=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$')
    segundo_nombre: str | None = Field(None, max_length=30, pattern=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]*$')
    apellidos: str = Field(..., max_length=60, pattern=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$')
    fecha_nacimiento: date
    genero: str = Field(..., description="Masculino, Femenino, No binario, Prefiero no reportar")
    correo_electronico: EmailStr
    celular: str = Field(..., min_length=10, max_length=10, pattern=r'^\d+$')

    @validator('tipo_documento')
    def validar_tipo_doc(cls, v):
        permitidos = ['Tarjeta de identidad', 'Cédula']
        if v not in permitidos:
            raise ValueError(f'Debe ser uno de: {permitidos}')
        return v

    @validator('genero')
    def validar_genero(cls, v):
        permitidos = ['Masculino', 'Femenino', 'No binario', 'Prefiero no reportar']
        if v not in permitidos:
            raise ValueError(f'Debe ser uno de: {permitidos}')
        return v