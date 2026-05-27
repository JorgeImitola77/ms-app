"""
El microservicio Crear define su propio ``PersonaCreate`` en
``ms-crear/schemas.py`` (con validadores distintos a los de ``shared.models``,
por ejemplo el patrón ASCII de nombres y la validación de tipo_documento como
``@validator``). Cubrimos ese schema aquí para que el coverage no caiga por
falta de tests sobre ese archivo y para garantizar que cualquier endpoint que
lo importe en el futuro mantenga las mismas garantías.
"""
from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

# El schema de ms-crear vive en un paquete con guion; lo importamos por path.
_PATH = Path(__file__).resolve().parent.parent / "ms-crear" / "schemas.py"
_spec = importlib.util.spec_from_file_location("ms_crear_schemas", _PATH)
ms_crear_schemas = importlib.util.module_from_spec(_spec)
sys.modules["ms_crear_schemas"] = ms_crear_schemas
_spec.loader.exec_module(ms_crear_schemas)
PersonaCreateLocal = ms_crear_schemas.PersonaCreate


def _base() -> dict:
    return {
        "nro_documento": "1234567890",
        "tipo_documento": "Cédula",
        "primer_nombre": "Carlos",
        "segundo_nombre": "Andres",
        "apellidos": "Perez Gomez",
        "fecha_nacimiento": date(1990, 5, 15),
        "genero": "Masculino",
        "correo_electronico": "carlos@example.com",
        "celular": "3001234567",
        "creado_por": str(uuid4()),
    }


def test_persona_create_local_caso_valido():
    p = PersonaCreateLocal(**_base())
    assert p.nro_documento == "1234567890"
    assert p.tipo_documento == "Cédula"


@pytest.mark.parametrize("valor", ["12345678901", "abc", "12a"])
def test_persona_create_local_nro_documento_invalido(valor):
    with pytest.raises(ValidationError):
        PersonaCreateLocal(**{**_base(), "nro_documento": valor})


@pytest.mark.parametrize("valor", ["Pasaporte", "CC", ""])
def test_persona_create_local_tipo_documento_invalido(valor):
    with pytest.raises(ValidationError):
        PersonaCreateLocal(**{**_base(), "tipo_documento": valor})


@pytest.mark.parametrize("valor", ["Otro", "M", ""])
def test_persona_create_local_genero_invalido(valor):
    with pytest.raises(ValidationError):
        PersonaCreateLocal(**{**_base(), "genero": valor})


def test_persona_create_local_celular_no_digitos():
    with pytest.raises(ValidationError):
        PersonaCreateLocal(**{**_base(), "celular": "abcdefghij"})


def test_persona_create_local_celular_longitud_invalida():
    with pytest.raises(ValidationError):
        PersonaCreateLocal(**{**_base(), "celular": "30012345"})


def test_persona_create_local_primer_nombre_con_acento_es_valido():
    """El patrón del schema local sí permite acentos y la ñ."""
    p = PersonaCreateLocal(**{**_base(), "primer_nombre": "María José"})
    assert p.primer_nombre == "María José"


def test_persona_create_local_primer_nombre_con_digitos_falla():
    with pytest.raises(ValidationError):
        PersonaCreateLocal(**{**_base(), "primer_nombre": "Carlos1"})


def test_persona_create_local_apellidos_max_60():
    PersonaCreateLocal(**{**_base(), "apellidos": "X" * 60})
    with pytest.raises(ValidationError):
        PersonaCreateLocal(**{**_base(), "apellidos": "X" * 61})


def test_persona_create_local_correo_invalido():
    with pytest.raises(ValidationError):
        PersonaCreateLocal(**{**_base(), "correo_electronico": "no-es-email"})


def test_modificar_schema_celular_valido_e_invalido():
    """Cubre también ``ms-modificar/schemas.py`` (PersonaUpdate local)."""
    path = Path(__file__).resolve().parent.parent / "ms-modificar" / "schemas.py"
    spec = importlib.util.spec_from_file_location("ms_modificar_schemas", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ms_modificar_schemas"] = mod
    spec.loader.exec_module(mod)

    upd = mod.PersonaUpdate(correo="x@y.co", celular="3001234567")
    assert upd.celular == "3001234567"
    with pytest.raises(ValidationError):
        mod.PersonaUpdate(celular="123")


def test_ms_consultar_schema_acepta_payload_completo():
    """Cubre ``ms-consultar/schemas.py`` (PersonaOut)."""
    path = Path(__file__).resolve().parent.parent / "ms-consultar" / "schemas.py"
    spec = importlib.util.spec_from_file_location("ms_consultar_schemas", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ms_consultar_schemas"] = mod
    spec.loader.exec_module(mod)

    out = mod.PersonaOut(
        nro_documento="1234567890",
        tipo_documento="Cédula",
        primer_nombre="Ana",
        apellidos="Lopez",
        fecha_nacimiento=date(1992, 3, 4),
        genero="Femenino",
        correo="ana@example.com",
        celular="3001112222",
    )
    assert out.foto_ruta is None
    assert out.segundo_nombre is None


def test_ms_log_schemas_log_rag_in_y_log_out():
    """Cubre ``ms-log/schemas.py`` (LogRagIn, LogOut)."""
    from datetime import datetime

    path = Path(__file__).resolve().parent.parent / "ms-log" / "schemas.py"
    spec = importlib.util.spec_from_file_location("ms_log_schemas", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ms_log_schemas"] = mod
    spec.loader.exec_module(mod)

    payload_in = mod.LogRagIn(pregunta_rag="q?", respuesta_rag="r.")
    assert payload_in.tipo_transaccion == "CONSULTA_RAG"  # default

    out = mod.LogOut(
        id_log=1,
        fecha_transaccion=datetime(2025, 1, 1),
        tipo_transaccion="CREAR",
        detalle="detalle",
    )
    assert out.documento_relacionado is None
    assert out.email_usuario is None
