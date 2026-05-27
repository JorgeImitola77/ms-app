"""
Tests del microservicio Log:
- ``GET /api/logs`` con y sin filtros (tipo / documento / fecha).
- ``POST /api/logs/internal`` (insert directo desde n8n / RAG).
"""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4


def _log_row(idx: int = 1) -> dict:
    return {
        "id_log": idx,
        "usuario_id": uuid4(),
        "email_usuario": f"user{idx}@example.com",
        "fecha_transaccion": datetime(2025, 1, 1, 12, 0, 0),
        "tipo_transaccion": "CREAR",
        "documento_relacionado": "1234567890",
        "pregunta_rag": None,
        "respuesta_rag": None,
        "detalle": "fila sintetica",
    }


# ---------------------------------------------------------------------------
# GET /api/logs
# ---------------------------------------------------------------------------
def test_logs_sin_filtros_retorna_lista(log_client):
    client, conn = log_client
    conn.fetch.return_value = [_log_row(1), _log_row(2)]

    resp = client.get("/api/logs")

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == 2
    assert body[0]["id_log"] == 1


def test_logs_filtra_por_tipo(log_client):
    client, conn = log_client
    conn.fetch.return_value = [_log_row(3)]

    resp = client.get("/api/logs", params={"tipo": "CREAR"})

    assert resp.status_code == 200
    # El SQL debe incluir el parámetro tipo_transaccion en la primera posición.
    call_args = conn.fetch.await_args
    sql = call_args.args[0]
    assert "tipo_transaccion = $1" in sql
    assert call_args.args[1] == "CREAR"


def test_logs_filtra_por_documento(log_client):
    client, conn = log_client
    conn.fetch.return_value = []

    resp = client.get("/api/logs", params={"documento": "9999999999"})

    assert resp.status_code == 200
    sql = conn.fetch.await_args.args[0]
    assert "documento_relacionado = $1" in sql
    assert conn.fetch.await_args.args[1] == "9999999999"


def test_logs_filtra_por_fecha_valida(log_client):
    client, conn = log_client
    conn.fetch.return_value = []

    resp = client.get("/api/logs", params={"fecha": "2025-01-15"})

    assert resp.status_code == 200
    sql = conn.fetch.await_args.args[0]
    assert "DATE(fecha_transaccion) = $1" in sql


def test_logs_combina_varios_filtros(log_client):
    client, conn = log_client
    conn.fetch.return_value = []

    resp = client.get(
        "/api/logs",
        params={"tipo": "CONSULTAR", "documento": "1234567890", "fecha": "2025-01-15"},
    )

    assert resp.status_code == 200
    sql = conn.fetch.await_args.args[0]
    assert "tipo_transaccion = $1" in sql
    assert "documento_relacionado = $2" in sql
    assert "DATE(fecha_transaccion) = $3" in sql


def test_logs_fecha_invalida_devuelve_400(log_client):
    """Validación: una fecha con formato distinto a YYYY-MM-DD debe devolver
    400 (no 500). El handler tiene un ``except HTTPException: raise`` antes
    del catch genérico para que esta validación propague intacta."""
    client, _ = log_client

    resp = client.get("/api/logs", params={"fecha": "15-01-2025"})

    assert resp.status_code == 400
    assert "YYYY-MM-DD" in resp.json()["detail"]


def test_logs_error_db_devuelve_500(log_client):
    client, conn = log_client
    conn.fetch.side_effect = RuntimeError("explota")

    resp = client.get("/api/logs")

    assert resp.status_code == 500
    assert "explota" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# POST /api/logs/internal
# ---------------------------------------------------------------------------
def test_log_internal_201_inserta_consulta_rag(log_client):
    client, conn = log_client
    conn.fetchval.return_value = 42

    payload = {
        "tipo_transaccion": "CONSULTA_RAG",
        "usuario_id": str(uuid4()),
        "pregunta_rag": "¿Cuántas personas hay?",
        "respuesta_rag": "5 personas",
    }
    resp = client.post("/api/logs/internal", json=payload)

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["status"] == "success"
    assert body["id_log"] == 42


def test_log_internal_usa_detalle_por_defecto_si_falta(log_client):
    client, conn = log_client
    conn.fetchval.return_value = 7

    resp = client.post(
        "/api/logs/internal",
        json={
            "tipo_transaccion": "CONSULTA_RAG",
            "pregunta_rag": "p?",
            "respuesta_rag": "r",
        },
    )

    assert resp.status_code == 201
    # El SQL recibe el detalle generado con la pregunta como sufijo.
    call_args = conn.fetchval.await_args
    detalle = call_args.args[-1]  # último parámetro en la query
    assert "Consulta RAG" in detalle


def test_log_internal_422_falta_pregunta(log_client):
    client, _ = log_client

    resp = client.post(
        "/api/logs/internal",
        json={"respuesta_rag": "sin pregunta"},
    )

    assert resp.status_code == 422
    assert any("pregunta_rag" in str(err) for err in resp.json()["detail"])


def test_log_internal_error_db_500(log_client):
    client, conn = log_client
    conn.fetchval.side_effect = RuntimeError("insert fail")

    resp = client.post(
        "/api/logs/internal",
        json={"pregunta_rag": "x", "respuesta_rag": "y"},
    )

    assert resp.status_code == 500
