"""
Tests unitarios para los modelos Pydantic de ``shared.models`` que codifican
los requisitos del RF9. Para cada constraint comprobamos un caso válido y al
menos uno inválido (recomendación explícita del documento de diseño, sec. 10).
"""
from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from shared.models import (
    LogEntry,
    LogQuery,
    PersonaCreate,
    PersonaResponse,
    PersonaUpdate,
)


def _persona_base() -> dict:
    """Carga base válida; cada test la modifica para apuntar a un campo."""
    return {
        "tipo_documento": "Cédula",
        "nro_documento": "1234567890",
        "primer_nombre": "Carlos",
        "segundo_nombre": "Andres",
        "apellidos": "Perez Gomez",
        "fecha_nacimiento": date(1990, 5, 15),
        "genero": "Masculino",
        "correo": "carlos@example.com",
        "celular": "3001234567",
    }


# ---------------------------------------------------------------------------
# PersonaCreate — caso 100% válido
# ---------------------------------------------------------------------------
def test_persona_create_caso_valido_completo():
    persona = PersonaCreate(**_persona_base())
    assert persona.nro_documento == "1234567890"
    assert persona.segundo_nombre == "Andres"


def test_persona_create_segundo_nombre_opcional_es_none():
    datos = _persona_base()
    datos.pop("segundo_nombre")
    persona = PersonaCreate(**datos)
    assert persona.segundo_nombre is None


# ---------------------------------------------------------------------------
# tipo_documento — Literal['Tarjeta de identidad', 'Cédula']
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("valor", ["Tarjeta de identidad", "Cédula"])
def test_tipo_documento_valores_permitidos(valor):
    datos = {**_persona_base(), "tipo_documento": valor}
    assert PersonaCreate(**datos).tipo_documento == valor


@pytest.mark.parametrize("valor", ["Pasaporte", "CC", "Cedula", "", "cédula"])
def test_tipo_documento_valor_invalido_falla(valor):
    datos = {**_persona_base(), "tipo_documento": valor}
    with pytest.raises(ValidationError) as exc:
        PersonaCreate(**datos)
    assert "tipo_documento" in str(exc.value)


# ---------------------------------------------------------------------------
# nro_documento — máximo 10 dígitos numéricos
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("valor", ["1", "1234567890", "9999999999"])
def test_nro_documento_valido(valor):
    datos = {**_persona_base(), "nro_documento": valor}
    assert PersonaCreate(**datos).nro_documento == valor


@pytest.mark.parametrize(
    "valor",
    ["12345678901", "abc", "12ab", "", "123-456"],
    ids=["once-digitos", "letras", "mixto", "vacio", "guion"],
)
def test_nro_documento_invalido(valor):
    datos = {**_persona_base(), "nro_documento": valor}
    with pytest.raises(ValidationError) as exc:
        PersonaCreate(**datos)
    assert "nro_documento" in str(exc.value)


# ---------------------------------------------------------------------------
# primer_nombre — max 30, sin dígitos
# ---------------------------------------------------------------------------
def test_primer_nombre_30_chars_es_valido():
    datos = {**_persona_base(), "primer_nombre": "A" * 30}
    assert PersonaCreate(**datos).primer_nombre == "A" * 30


def test_primer_nombre_31_chars_falla():
    datos = {**_persona_base(), "primer_nombre": "A" * 31}
    with pytest.raises(ValidationError) as exc:
        PersonaCreate(**datos)
    assert "primer_nombre" in str(exc.value)


@pytest.mark.parametrize("valor", ["Carlos1", "1Carlos", "Carlo5"])
def test_primer_nombre_con_digitos_falla(valor):
    datos = {**_persona_base(), "primer_nombre": valor}
    with pytest.raises(ValidationError):
        PersonaCreate(**datos)


# ---------------------------------------------------------------------------
# segundo_nombre — opcional pero con las mismas reglas si se envía
# ---------------------------------------------------------------------------
def test_segundo_nombre_con_digitos_falla():
    datos = {**_persona_base(), "segundo_nombre": "Pedro2"}
    with pytest.raises(ValidationError) as exc:
        PersonaCreate(**datos)
    assert "segundo_nombre" in str(exc.value)


def test_segundo_nombre_31_chars_falla():
    datos = {**_persona_base(), "segundo_nombre": "B" * 31}
    with pytest.raises(ValidationError):
        PersonaCreate(**datos)


# ---------------------------------------------------------------------------
# apellidos — max 60, sin dígitos
# ---------------------------------------------------------------------------
def test_apellidos_60_chars_es_valido():
    datos = {**_persona_base(), "apellidos": "X" * 60}
    assert PersonaCreate(**datos).apellidos == "X" * 60


def test_apellidos_61_chars_falla():
    datos = {**_persona_base(), "apellidos": "X" * 61}
    with pytest.raises(ValidationError) as exc:
        PersonaCreate(**datos)
    assert "apellidos" in str(exc.value)


def test_apellidos_con_digitos_falla():
    datos = {**_persona_base(), "apellidos": "Perez 123"}
    with pytest.raises(ValidationError):
        PersonaCreate(**datos)


# ---------------------------------------------------------------------------
# genero — Literal con 4 valores
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "valor", ["Masculino", "Femenino", "No binario", "Prefiero no reportar"]
)
def test_genero_valores_permitidos(valor):
    datos = {**_persona_base(), "genero": valor}
    assert PersonaCreate(**datos).genero == valor


@pytest.mark.parametrize("valor", ["masculino", "M", "Otro", ""])
def test_genero_valor_invalido_falla(valor):
    datos = {**_persona_base(), "genero": valor}
    with pytest.raises(ValidationError) as exc:
        PersonaCreate(**datos)
    assert "genero" in str(exc.value)


# ---------------------------------------------------------------------------
# correo — EmailStr
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "valor", ["a@b.co", "carlos.perez@example.com", "user+tag@dominio.io"]
)
def test_correo_valido(valor):
    datos = {**_persona_base(), "correo": valor}
    assert PersonaCreate(**datos).correo == valor


@pytest.mark.parametrize(
    "valor", ["sin-arroba.com", "espacio @b.com", "a@", "@b.com", ""]
)
def test_correo_invalido(valor):
    datos = {**_persona_base(), "correo": valor}
    with pytest.raises(ValidationError) as exc:
        PersonaCreate(**datos)
    assert "correo" in str(exc.value).lower()


# ---------------------------------------------------------------------------
# celular — exactamente 10 dígitos
# ---------------------------------------------------------------------------
def test_celular_10_digitos_es_valido():
    datos = {**_persona_base(), "celular": "3001234567"}
    assert PersonaCreate(**datos).celular == "3001234567"


@pytest.mark.parametrize(
    "valor",
    ["300123456", "30012345678", "300-123456", "abcdefghij", ""],
    ids=["nueve", "once", "guion", "letras", "vacio"],
)
def test_celular_invalido(valor):
    datos = {**_persona_base(), "celular": valor}
    with pytest.raises(ValidationError) as exc:
        PersonaCreate(**datos)
    assert "celular" in str(exc.value)


# ---------------------------------------------------------------------------
# fecha_nacimiento — date
# ---------------------------------------------------------------------------
def test_fecha_nacimiento_iso_string_se_convierte():
    datos = {**_persona_base(), "fecha_nacimiento": "1995-03-20"}
    persona = PersonaCreate(**datos)
    assert persona.fecha_nacimiento == date(1995, 3, 20)


def test_fecha_nacimiento_formato_invalido_falla():
    datos = {**_persona_base(), "fecha_nacimiento": "20-03-1995"}
    with pytest.raises(ValidationError):
        PersonaCreate(**datos)


# ---------------------------------------------------------------------------
# PersonaUpdate — todos los campos opcionales, mismas reglas si se envían
# ---------------------------------------------------------------------------
def test_persona_update_acepta_payload_vacio():
    PersonaUpdate()  # no debe lanzar


def test_persona_update_solo_correo_y_celular():
    upd = PersonaUpdate(correo="x@y.co", celular="3009998877")
    assert upd.correo == "x@y.co"
    assert upd.celular == "3009998877"


def test_persona_update_correo_invalido_falla():
    with pytest.raises(ValidationError):
        PersonaUpdate(correo="no-es-email")


def test_persona_update_celular_invalido_falla():
    with pytest.raises(ValidationError):
        PersonaUpdate(celular="123")


def test_persona_update_primer_nombre_con_digitos_falla():
    with pytest.raises(ValidationError):
        PersonaUpdate(primer_nombre="Ana1")


def test_persona_update_genero_invalido_falla():
    with pytest.raises(ValidationError):
        PersonaUpdate(genero="otra")


# ---------------------------------------------------------------------------
# PersonaResponse — incluye foto_ruta opcional y fecha_registro
# ---------------------------------------------------------------------------
def test_persona_response_acepta_fecha_registro():
    from datetime import datetime

    datos = {**_persona_base(), "fecha_registro": datetime(2025, 1, 1, 12)}
    resp = PersonaResponse(**datos)
    assert resp.foto_ruta is None
    assert resp.fecha_registro.year == 2025


# ---------------------------------------------------------------------------
# LogEntry / LogQuery
# ---------------------------------------------------------------------------
def test_log_entry_basico_valido():
    from datetime import datetime

    entry = LogEntry(
        id_log=1,
        fecha_transaccion=datetime(2025, 1, 1, 10, 30),
        tipo_transaccion="CREAR",
        documento_relacionado="1234567890",
        detalle="Creación exitosa",
    )
    assert entry.id_log == 1
    assert entry.tipo_transaccion == "CREAR"


def test_log_entry_documento_es_opcional():
    from datetime import datetime

    entry = LogEntry(
        id_log=2,
        fecha_transaccion=datetime(2025, 1, 1, 10, 30),
        tipo_transaccion="CONSULTA_RAG",
        detalle="Consulta RAG",
    )
    assert entry.documento_relacionado is None


def test_log_query_todos_los_campos_opcionales():
    LogQuery()  # no lanza
    q = LogQuery(
        tipo_transaccion="CREAR",
        documento_relacionado="1234567890",
        fecha_inicio=date(2025, 1, 1),
        fecha_fin=date(2025, 1, 31),
    )
    assert q.tipo_transaccion == "CREAR"
    assert q.fecha_fin == date(2025, 1, 31)


def test_log_query_fecha_invalida_falla():
    with pytest.raises(ValidationError):
        LogQuery(fecha_inicio="no-es-fecha")
