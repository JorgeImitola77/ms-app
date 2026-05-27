"""
Tests del microservicio Modificar (``PATCH /api/personas/{documento}``).
Casos: éxito 200, 404 documento no encontrado, 400 payload vacío y errores
de validación Pydantic.
"""
from __future__ import annotations


def test_modificar_persona_200_exito(modificar_client):
    client, conn = modificar_client
    # La persona existe (fetchval para EXISTS devuelve 1)
    # y el usuario_id se resuelve para el log.
    conn.fetchval.side_effect = [
        1,  # SELECT 1 FROM personas WHERE nro_documento = ...
        "11111111-1111-1111-1111-111111111111",  # SELECT usuario_id FROM usuarios
    ]

    resp = client.patch(
        "/api/personas/1234567890",
        json={"correo": "nuevo@example.com", "celular": "3009998877"},
    )

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "success"
    # Debe ejecutar 2 statements: UPDATE personas + INSERT log.
    assert conn.execute.await_count == 2


def test_modificar_persona_404_documento_inexistente(modificar_client):
    client, conn = modificar_client
    conn.fetchval.return_value = None  # SELECT 1 ... no encuentra fila

    resp = client.patch(
        "/api/personas/0000000000",
        json={"correo": "x@y.co"},
    )

    assert resp.status_code == 404
    assert "no encontrada" in resp.json()["detail"].lower()


def test_modificar_persona_400_sin_campos_a_actualizar(modificar_client):
    client, _ = modificar_client

    resp = client.patch("/api/personas/1234567890", json={})

    assert resp.status_code == 400
    assert "actualizar" in resp.json()["detail"].lower()


def test_modificar_persona_celular_invalido_es_422(modificar_client):
    client, _ = modificar_client

    resp = client.patch(
        "/api/personas/1234567890",
        json={"celular": "no-son-digitos"},
    )

    assert resp.status_code == 422
    assert any("celular" in str(err) for err in resp.json()["detail"])


def test_modificar_persona_nombre_con_digitos_es_422(modificar_client):
    client, _ = modificar_client

    resp = client.patch(
        "/api/personas/1234567890",
        json={"primer_nombre": "Carlos1"},
    )

    assert resp.status_code == 422


def test_modificar_persona_error_db_devuelve_500(modificar_client):
    """Errores inesperados → 500 amigable sin filtrar ``str(exc)``."""
    client, conn = modificar_client
    conn.fetchval.side_effect = RuntimeError("db caida")

    resp = client.patch(
        "/api/personas/1234567890",
        json={"correo": "x@y.co"},
    )

    assert resp.status_code == 500
    detail = resp.json()["detail"]
    assert "db caida" not in detail
    assert "error interno" in detail.lower()


def test_modificar_persona_db_caida_devuelve_503(modificar_client):
    """BD inaccesible → 503 con mensaje amigable."""
    client, conn = modificar_client
    conn.fetchval.side_effect = ConnectionError("refused")

    resp = client.patch(
        "/api/personas/1234567890",
        json={"correo": "x@y.co"},
    )

    assert resp.status_code == 503
    assert "base de datos" in resp.json()["detail"].lower()
