import pytest
from pydantic import ValidationError
from datetime import date
from shared.models import PersonaCreate

def test_persona_create_valido():
    # Caso válido: Todos los datos cumplen las reglas
    datos = {
        "tipo_documento": "Cédula",
        "nro_documento": "1234567890",
        "primer_nombre": "Carlos",
        "apellidos": "Perez Gomez",
        "fecha_nacimiento": date(1990, 5, 15),
        "genero": "Masculino",
        "correo": "carlos@example.com",
        "celular": "3001234567"
    }
    persona = PersonaCreate(**datos)
    assert persona.nro_documento == "1234567890"

def test_persona_create_invalido_nombres_con_numeros():
    # Caso inválido: El nombre tiene números (falla el regex)
    datos = {
        "tipo_documento": "Cédula",
        "nro_documento": "12345",
        "primer_nombre": "Carlos123", # <--- ERROR AQUÍ
        "apellidos": "Perez",
        "fecha_nacimiento": date(1990, 5, 15),
        "genero": "Masculino",
        "correo": "carlos@example.com",
        "celular": "3001234567"
    }
    with pytest.raises(ValidationError) as excinfo:
        PersonaCreate(**datos)
    
    # Verificamos que Pydantic atrapó el error en el campo primer_nombre
    assert "primer_nombre" in str(excinfo.value)

def test_persona_create_invalido_celular():
    # Caso inválido: Celular de 11 dígitos en lugar de 10
    datos = {
        "tipo_documento": "Cédula",
        "nro_documento": "12345",
        "primer_nombre": "Carlos",
        "apellidos": "Perez",
        "fecha_nacimiento": date(1990, 5, 15),
        "genero": "Masculino",
        "correo": "carlos@example.com",
        "celular": "30012345678" # <--- ERROR AQUÍ
    }
    with pytest.raises(ValidationError):
        PersonaCreate(**datos)

def test_persona_create_invalido_correo():
    # Caso inválido: Formato de correo incorrecto
    datos = {
        "tipo_documento": "Tarjeta de identidad",
        "nro_documento": "123",
        "primer_nombre": "Ana",
        "apellidos": "Gomez",
        "fecha_nacimiento": date(2010, 1, 1),
        "genero": "Femenino",
        "correo": "correo_sin_arroba.com", # <--- ERROR AQUÍ
        "celular": "3001234567"
    }
    with pytest.raises(ValidationError):
        PersonaCreate(**datos)