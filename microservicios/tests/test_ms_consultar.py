"""
Tests del microservicio Consultar (``GET /api/personas/{documento}``).
Casos: éxito 200 con datos completos, 404 documento no encontrado, 500 error DB.
"""
from __future__ import annotations


def test_consultar_persona_200_devuelve_datos(consultar_client, persona_db_row):
    client, conn = consultar_client
    conn.fetchrow.return_value = persona_db_row
    conn.fetchval.return_value = "11111111-1111-1111-1111-111111111111"

    resp = client.get("/api/personas/1234567890")

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["nro_documento"] == persona_db_row["nro_documento"]
    assert body["primer_nombre"] == persona_db_row["primer_nombre"]
    # Debe insertar un log de la consulta.
    assert conn.execute.await_count == 1


def test_consultar_persona_404_no_encontrada(consultar_client):
    client, conn = consultar_client
    conn.fetchrow.return_value = None

    resp = client.get("/api/personas/0000000000")

    assert resp.status_code == 404
    assert "no encontrada" in resp.json()["detail"].lower()


def test_consultar_persona_error_db_devuelve_500(consultar_client):
    client, conn = consultar_client
    conn.fetchrow.side_effect = RuntimeError("timeout")

    resp = client.get("/api/personas/1234567890")

    assert resp.status_code == 500
    assert "timeout" in resp.json()["detail"]
