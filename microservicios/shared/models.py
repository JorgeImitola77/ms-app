from pydantic import BaseModel, Field, EmailStr
from typing import Literal, Optional
from datetime import date, datetime

# ==========================================
# MODELOS DE PERSONA
# ==========================================

class PersonaCreate(BaseModel):
    """Datos requeridos para crear una nueva persona."""

    model_config = {
        "json_schema_extra": {
            "example": {
                "tipo_documento": "Cédula",
                "nro_documento": "1003377298",
                "primer_nombre": "Zenen",
                "segundo_nombre": "Andrés",
                "apellidos": "Contreras Royero",
                "fecha_nacimiento": "2000-05-15",
                "genero": "Masculino",
                "correo": "zenen@ejemplo.com",
                "celular": "3001234567",
            }
        }
    }

    tipo_documento: Literal['Tarjeta de identidad', 'Cédula'] = Field(
        description='Tipo de documento. Valores: `"Tarjeta de identidad"` ó `"Cédula"`.'
    )
    nro_documento: str = Field(
        pattern=r'^[0-9]{1,10}$',
        description="Número de documento. Solo dígitos, entre 1 y 10 caracteres.",
        example="1003377298",
    )
    primer_nombre: str = Field(
        max_length=30,
        pattern=r'^[^0-9]+$',
        description="Primer nombre. Máx. 30 caracteres, sin dígitos.",
        example="Zenen",
    )
    segundo_nombre: Optional[str] = Field(
        default=None,
        max_length=30,
        pattern=r'^[^0-9]+$',
        description="Segundo nombre (opcional). Máx. 30 caracteres, sin dígitos.",
        example="Andrés",
    )
    apellidos: str = Field(
        max_length=60,
        pattern=r'^[^0-9]+$',
        description="Apellidos. Máx. 60 caracteres, sin dígitos.",
        example="Contreras Royero",
    )
    fecha_nacimiento: date = Field(
        description="Fecha de nacimiento en formato `YYYY-MM-DD`.",
        example="2000-05-15",
    )
    genero: Literal['Masculino', 'Femenino', 'No binario', 'Prefiero no reportar'] = Field(
        description='Género. Valores: `"Masculino"`, `"Femenino"`, `"No binario"`, `"Prefiero no reportar"`.'
    )
    correo: EmailStr = Field(
        description="Dirección de correo electrónico válida.",
        example="zenen@ejemplo.com",
    )
    celular: str = Field(
        pattern=r'^[0-9]{10}$',
        description="Número de celular. Exactamente 10 dígitos numéricos.",
        example="3001234567",
    )


class PersonaUpdate(BaseModel):
    """
    Campos actualizables de una persona. Todos son opcionales; envía únicamente
    los que deseas cambiar. El `nro_documento` no puede modificarse (es la PK).
    """

    tipo_documento: Optional[Literal['Tarjeta de identidad', 'Cédula']] = Field(
        default=None,
        description='Tipo de documento. Valores: `"Tarjeta de identidad"` ó `"Cédula"`.',
    )
    primer_nombre: Optional[str] = Field(
        default=None,
        max_length=30,
        pattern=r'^[^0-9]+$',
        description="Primer nombre. Máx. 30 caracteres, sin dígitos.",
        example="Zenen",
    )
    segundo_nombre: Optional[str] = Field(
        default=None,
        max_length=30,
        pattern=r'^[^0-9]+$',
        description="Segundo nombre. Máx. 30 caracteres, sin dígitos.",
        example="Andrés",
    )
    apellidos: Optional[str] = Field(
        default=None,
        max_length=60,
        pattern=r'^[^0-9]+$',
        description="Apellidos. Máx. 60 caracteres, sin dígitos.",
        example="Contreras Royero",
    )
    fecha_nacimiento: Optional[date] = Field(
        default=None,
        description="Fecha de nacimiento en formato `YYYY-MM-DD`.",
        example="2000-05-15",
    )
    genero: Optional[Literal['Masculino', 'Femenino', 'No binario', 'Prefiero no reportar']] = Field(
        default=None,
        description='Género. Valores: `"Masculino"`, `"Femenino"`, `"No binario"`, `"Prefiero no reportar"`.',
    )
    correo: Optional[EmailStr] = Field(
        default=None,
        description="Dirección de correo electrónico válida.",
        example="nuevo@correo.com",
    )
    celular: Optional[str] = Field(
        default=None,
        pattern=r'^[0-9]{10}$',
        description="Número de celular. Exactamente 10 dígitos.",
        example="3109876543",
    )


class PersonaResponse(PersonaCreate):
    """Respuesta completa de una persona incluyendo campos generados por el servidor."""

    foto_ruta: Optional[str] = Field(
        default=None,
        description="Ruta interna del servidor donde se almacena la foto de perfil.",
        example="/app/uploads/1003377298.jpg",
    )
    fecha_registro: datetime = Field(
        description="Fecha y hora en que se creó el registro (UTC).",
        example="2025-05-26T14:30:00",
    )


# ==========================================
# MODELOS DE LOGS
# ==========================================

class LogEntry(BaseModel):
    """Entrada individual del historial de auditoría."""

    model_config = {
        "json_schema_extra": {
            "example": {
                "id_log": 42,
                "fecha_transaccion": "2025-05-26T14:30:00",
                "tipo_transaccion": "CREAR",
                "documento_relacionado": "1003377298",
                "detalle": "Creación exitosa de Zenen Contreras Royero",
            }
        }
    }

    id_log: int = Field(description="Identificador único autoincremental del log.")
    fecha_transaccion: datetime = Field(description="Fecha y hora de la transacción (UTC).")
    tipo_transaccion: str = Field(
        description="Tipo de operación: `CREAR`, `CONSULTAR`, `MODIFICAR`, `BORRAR`, `CONSULTA_RAG`."
    )
    documento_relacionado: Optional[str] = Field(
        default=None,
        description="Número de documento afectado por la transacción (si aplica).",
    )
    detalle: str = Field(description="Descripción legible de la operación realizada.")


class LogQuery(BaseModel):
    """Filtros opcionales para la consulta de logs."""

    model_config = {
        "json_schema_extra": {
            "example": {
                "tipo_transaccion": "CREAR",
                "documento_relacionado": "1003377298",
                "fecha_inicio": "2025-05-01",
                "fecha_fin": "2025-05-31",
            }
        }
    }

    tipo_transaccion: Optional[str] = Field(
        default=None,
        description="Filtrar por tipo de transacción.",
        example="CREAR",
    )
    documento_relacionado: Optional[str] = Field(
        default=None,
        description="Filtrar por número de documento relacionado.",
        example="1003377298",
    )
    fecha_inicio: Optional[date] = Field(
        default=None,
        description="Fecha de inicio del rango de búsqueda (inclusive).",
        example="2025-05-01",
    )
    fecha_fin: Optional[date] = Field(
        default=None,
        description="Fecha de fin del rango de búsqueda (inclusive).",
        example="2025-05-31",
    )
