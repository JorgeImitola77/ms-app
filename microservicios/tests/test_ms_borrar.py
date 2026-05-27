"""
Tests del microservicio Borrar (``DELETE /api/personas/{documento}``).
Casos: éxito 200, 404 no encontrado, 500 error.
"""
from __future__ import annotations


def test_borrar_persona_200_exito(borrar_client):
    client, conn = borrar_client
    conn.fetchval.side_effect = [
        1,  # SELECT 1 FROM personas ... -> existe
        "11111111-1111-1111-1111-111111111111",  # SELECT usuario_id FROM usuarios
    ]

    resp = client.delete("/api/personas/1234567890")

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "success"
    assert "1234567890" in body["message"]
    # DELETE persona + INSERT log
    assert conn.execute.await_count == 2


def test_borrar_persona_404_no_existe(borrar_client):
    client, conn = borrar_client
    conn.fetchval.return_value = None

    resp = client.delete("/api/personas/0000000000")

    assert resp.status_code == 404
    assert "no encontrada" in resp.json()["detail"].lower()


def test_borrar_persona_error_db_devuelve_500(borrar_client):
    client, conn = borrar_client
    conn.fetchval.side_effect = RuntimeError("conn perdida")

    resp = client.delete("/api/personas/1234567890")

    assert resp.status_code == 500
    assert "conn perdida" in resp.json()["detail"]
