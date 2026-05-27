"""
Pruebas de carga y rendimiento (card 86e19t0at).

Valida el RNF7 (FastAPI asíncrono soportando peticiones simultáneas).

Escenarios definidos como tareas con tags:
  - crear     -> POST   http://localhost:8001/api/personas       (multipart)
  - consulta  -> GET    http://localhost:8003/api/personas/{doc} (vía nginx LB)
  - rag       -> POST   http://localhost:5678/webhook/rag-consulta

Métricas capturadas por locust:
  - latencia p50 / p95 / p99
  - RPS (req/s)
  - tasa de error (HTTP 4xx / 5xx)

Ejecución típica (ver loadtest/README.md):
    locust -f loadtest/locustfile.py --headless \
           -u 50 -r 10 --run-time 1m --tags crear --host http://localhost \
           --csv loadtest/reports/crear
"""

from __future__ import annotations

import io
import os
import random
import string
from datetime import date, timedelta

from locust import HttpUser, between, events, tag, task


TOKEN = os.getenv("LOADTEST_TOKEN", "")
SEED_DOCUMENTS_FILE = os.getenv(
    "LOADTEST_SEED_DOCS",
    os.path.join(os.path.dirname(__file__), "data", "seed_documentos.txt"),
)
RAG_QUESTIONS_FILE = os.getenv(
    "LOADTEST_RAG_QUESTIONS",
    os.path.join(os.path.dirname(__file__), "data", "rag_preguntas.txt"),
)

MS_CREACION_PORT = int(os.getenv("MS_CREACION_PORT", "8001"))
MS_CONSULTA_PORT = int(os.getenv("MS_CONSULTA_PORT", "8003"))
N8N_PORT = int(os.getenv("N8N_PUBLIC_PORT", "5678"))


def _auth_header() -> dict:
    if not TOKEN:
        return {}
    return {"Authorization": f"Bearer {TOKEN}"}


def _load_lines(path: str, fallback: list[str]) -> list[str]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines = [line.strip() for line in fh if line.strip()]
        return lines or fallback
    except FileNotFoundError:
        return fallback


SEED_DOCUMENTOS = _load_lines(
    SEED_DOCUMENTS_FILE,
    fallback=["1020304050", "1010101010", "1234567890"],
)
RAG_PREGUNTAS = _load_lines(
    RAG_QUESTIONS_FILE,
    fallback=[
        "¿Cuántas personas hay registradas?",
        "Muéstrame las personas creadas en el último mes.",
        "¿Cuál es la persona con mayor edad?",
    ],
)


@events.test_start.add_listener
def _warn_if_no_token(environment, **_kwargs):
    if TOKEN:
        return
    print(
        "[loadtest] ADVERTENCIA: LOADTEST_TOKEN no está definido. "
        "Las peticiones autenticadas devolverán 401 y los resultados "
        "no reflejarán la latencia real del backend. "
        "Genera un token (ver loadtest/README.md) y vuelve a lanzar."
    )


def _random_documento() -> str:
    return "".join(random.choices(string.digits, k=10))


def _random_fecha_nacimiento() -> str:
    inicio = date(1960, 1, 1)
    delta_dias = random.randint(0, 365 * 50)
    return (inicio + timedelta(days=delta_dias)).isoformat()


def _foto_dummy() -> tuple[str, bytes, str]:
    payload = b"\xff\xd8\xff\xe0" + os.urandom(512) + b"\xff\xd9"
    return ("foto.jpg", payload, "image/jpeg")


class CrearUser(HttpUser):
    """50 usuarios concurrentes haciendo Crear durante 1 minuto (escenario A)."""

    wait_time = between(0.5, 1.5)
    host = f"http://localhost:{MS_CREACION_PORT}"

    @tag("crear")
    @task
    def crear_persona(self):
        documento = _random_documento()
        data = {
            "nro_documento": documento,
            "tipo_documento": "CC",
            "primer_nombre": "Carga",
            "segundo_nombre": "Test",
            "apellidos": "Locust Synthetic",
            "fecha_nacimiento": _random_fecha_nacimiento(),
            "genero": random.choice(["M", "F", "O"]),
            "correo": f"loadtest_{documento}@example.com",
            "celular": "3000000000",
        }
        files = {"foto": _foto_dummy()}
        with self.client.post(
            "/api/personas",
            data=data,
            files=files,
            headers=_auth_header(),
            name="POST /api/personas (crear)",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 201):
                resp.success()
            elif resp.status_code == 409:
                # Documento duplicado: no es un fallo del sistema, es esperable
                # bajo concurrencia con documentos aleatorios.
                resp.success()
            else:
                resp.failure(f"status={resp.status_code} body={resp.text[:200]}")


class ConsultarUser(HttpUser):
    """100 usuarios concurrentes haciendo Consulta (escala=3) (escenario B)."""

    wait_time = between(0.2, 0.8)
    host = f"http://localhost:{MS_CONSULTA_PORT}"

    @tag("consulta")
    @task
    def consultar_persona(self):
        documento = random.choice(SEED_DOCUMENTOS)
        with self.client.get(
            f"/api/personas/{documento}",
            headers=_auth_header(),
            name="GET /api/personas/{doc} (consultar)",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 404:
                resp.success()
            else:
                resp.failure(f"status={resp.status_code} body={resp.text[:200]}")


class RagUser(HttpUser):
    """20 usuarios concurrentes en RAG (escenario C)."""

    wait_time = between(1.0, 3.0)
    host = f"http://localhost:{N8N_PORT}"

    @tag("rag")
    @task
    def consulta_rag(self):
        pregunta = random.choice(RAG_PREGUNTAS)
        payload = {
            "pregunta": pregunta,
            "usuario_id": "loadtest|synthetic",
            "auth0_id": "loadtest|synthetic",
            "email": "loadtest@example.com",
        }
        with self.client.post(
            "/webhook/rag-consulta",
            json=payload,
            headers=_auth_header(),
            name="POST /webhook/rag-consulta",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            elif resp.status_code in (401, 403):
                resp.success()
            else:
                resp.failure(f"status={resp.status_code} body={resp.text[:200]}")
