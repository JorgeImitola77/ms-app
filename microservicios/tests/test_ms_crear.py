"""
Tests del microservicio Crear (``POST /api/personas``).

Casos cubiertos (alineados con el card 86e19rzwg):

- 201 — creación exitosa con todos los campos obligatorios.
- 201 — auto-registro del usuario nuevo en la tabla ``usuarios``.
- 422 — FastAPI valida los ``Form(...)`` obligatorios faltantes.
- 400 — ``UniqueViolationError`` cuando el documento ya existe en la BD.
  (El card pide 409; el código actual devuelve 400 — se documenta en el
  README de tests. Aquí afirmamos el comportamiento real.)
- 500 — error genérico en la BD se traduce a 500.
"""
from __future__ import annotations

import asyncpg


def _form_persona() -> dict:
    return {
        "nro_documento": "1234567890",
        "tipo_documento": "Cédula",
        "primer_nombre": "Carlos",
        "segundo_nombre": "Andres",
        "apellidos": "Perez Gomez",
        "fecha_nacimiento": "1990-05-15",
        "genero": "Masculino",
        "correo": "carlos@example.com",
        "celular": "3001234567",
    }


def test_crear_persona_201_exito_usuario_existente(crear_client):
    client, conn = crear_client
    # Usuario ya registrado en la tabla usuarios -> no auto-registro.
    conn.fetchrow.return_value = {
        "usuario_id": "11111111-1111-1111-1111-111111111111",
        "email": "test@example.com",
    }

    resp = client.post("/api/personas", data=_form_persona())

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["status"] == "success"
    # Debe haber dos INSERT: persona + log.
    assert conn.execute.await_count >= 2


def test_crear_persona_auto_registra_usuario_si_no_existe(crear_client):
    client, conn = crear_client
    # El SELECT por auth0_id no encuentra usuario.
    conn.fetchrow.return_value = None
    # El INSERT...RETURNING usuario_id devuelve un UUID nuevo.
    conn.fetchval.return_value = "22222222-2222-2222-2222-222222222222"

    resp = client.post("/api/personas", data=_form_persona())

    assert resp.status_code == 201, resp.text
    # fetchval se usa exactamente una vez para auto-registrar al usuario.
    assert conn.fetchval.await_count == 1


def test_crear_persona_422_falta_campo_obligatorio(crear_client):
    client, _ = crear_client
    datos = _form_persona()
    datos.pop("celular")  # campo Form requerido

    resp = client.post("/api/personas", data=datos)

    assert resp.status_code == 422
    # FastAPI indica explícitamente el campo faltante.
    assert any("celular" in str(err) for err in resp.json()["detail"])


def test_crear_persona_documento_duplicado_devuelve_400(crear_client):
    """El card 86e19rzwg pide 409; el código real devuelve 400 al capturar
    ``UniqueViolationError``. Verificamos el comportamiento actual y el
    README explica la discrepancia para una futura corrección."""
    client, conn = crear_client
    conn.fetchrow.return_value = {
        "usuario_id": "11111111-1111-1111-1111-111111111111",
        "email": "test@example.com",
    }
    conn.execute.side_effect = asyncpg.exceptions.UniqueViolationError(
        "duplicate key"
    )

    resp = client.post("/api/personas", data=_form_persona())

    assert resp.status_code == 400
    assert "ya se encuentra registrado" in resp.json()["detail"]


def test_crear_persona_error_generico_devuelve_500(crear_client):
    client, conn = crear_client
    conn.fetchrow.side_effect = RuntimeError("boom")

    resp = client.post("/api/personas", data=_form_persona())

    assert resp.status_code == 500
    assert "boom" in resp.json()["detail"]


def test_crear_persona_acepta_foto_dentro_del_limite(crear_client, tmp_path):
    client, conn = crear_client
    conn.fetchrow.return_value = {
        "usuario_id": "11111111-1111-1111-1111-111111111111",
        "email": "test@example.com",
    }
    foto_bytes = b"\x89PNG\r\n\x1a\n" + b"0" * 1024  # ~1KB, bien por debajo de 2MB

    resp = client.post(
        "/api/personas",
        data=_form_persona(),
        files={"foto": ("avatar.png", foto_bytes, "image/png")},
    )

    assert resp.status_code == 201, resp.text


def test_crear_persona_rechaza_foto_mayor_a_2mb(crear_client):
    client, conn = crear_client
    conn.fetchrow.return_value = {
        "usuario_id": "11111111-1111-1111-1111-111111111111",
        "email": "test@example.com",
    }
    foto_grande = b"x" * (2 * 1024 * 1024 + 1)  # 2MB + 1 byte

    resp = client.post(
        "/api/personas",
        data=_form_persona(),
        files={"foto": ("grande.png", foto_grande, "image/png")},
    )

    assert resp.status_code == 422
    assert "2 MB" in resp.json()["detail"]


def test_test_db_endpoint_responde(crear_client):
    """``GET /test-db`` no debe lanzar; con conn mockeada responde 200 con la
    versión sintética que devolvamos."""
    client, conn = crear_client
    conn.fetchval.return_value = "PostgreSQL 16.0 (fake)"

    resp = client.get("/test-db")

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "PostgreSQL" in body["db_version"]
