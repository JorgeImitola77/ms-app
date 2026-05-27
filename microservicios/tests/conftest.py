"""Fixtures compartidos por todos los tests de microservicios."""
from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from tests.helpers import FakeConnection, load_service, override_auth, patch_db

# Mismo path que el conftest raíz usa para parchear /app/uploads. Cualquier
# acceso a UPLOAD_DIR durante un test escribe aquí.
TEST_UPLOAD_DIR = Path(tempfile.gettempdir()) / "ms_app_test_uploads"
TEST_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Datos de ejemplo reutilizables
# ---------------------------------------------------------------------------
@pytest.fixture
def persona_valida() -> dict[str, Any]:
    return {
        "tipo_documento": "Cédula",
        "nro_documento": "1234567890",
        "primer_nombre": "Carlos",
        "segundo_nombre": "Andres",
        "apellidos": "Perez Gomez",
        "fecha_nacimiento": "1990-05-15",
        "genero": "Masculino",
        "correo": "carlos@example.com",
        "celular": "3001234567",
    }


@pytest.fixture
def persona_db_row(persona_valida: dict[str, Any]) -> dict[str, Any]:
    """Lo que devuelve `SELECT * FROM personas` (incluye foto_ruta y fecha_registro)."""
    from datetime import date

    row = dict(persona_valida)
    row["fecha_nacimiento"] = date.fromisoformat(row["fecha_nacimiento"])
    row["foto_ruta"] = None
    row["fecha_registro"] = datetime(2025, 1, 1, 12, 0, 0)
    return row


# ---------------------------------------------------------------------------
# Cargadores de cada microservicio (cachean por sesión para no re-importar)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def ms_crear_module():
    mod = load_service("ms-crear")
    # UPLOAD_DIR está cableado a /app/uploads (ruta del contenedor); en tests
    # locales redirigimos a un tempdir escribible para permitir guardar fotos.
    mod.UPLOAD_DIR = str(TEST_UPLOAD_DIR)
    return mod


@pytest.fixture(scope="session")
def ms_modificar_module():
    return load_service("ms-modificar")


@pytest.fixture(scope="session")
def ms_consultar_module():
    mod = load_service("ms-consultar")
    mod.UPLOAD_DIR = str(TEST_UPLOAD_DIR)
    return mod


@pytest.fixture(scope="session")
def ms_borrar_module():
    return load_service("ms-borrar")


@pytest.fixture(scope="session")
def ms_log_module():
    return load_service("ms-log")


# ---------------------------------------------------------------------------
# Builders de TestClient con DB y auth mockeadas
# ---------------------------------------------------------------------------
def _build_client(module, conn: FakeConnection):
    from fastapi.testclient import TestClient

    patch_db(module, conn)
    override_auth(module.app)
    return TestClient(module.app), conn


@pytest.fixture
def fake_conn() -> FakeConnection:
    return FakeConnection()


@pytest.fixture
def crear_client(ms_crear_module, fake_conn):
    yield _build_client(ms_crear_module, fake_conn)
    ms_crear_module.app.dependency_overrides.clear()


@pytest.fixture
def modificar_client(ms_modificar_module, fake_conn):
    yield _build_client(ms_modificar_module, fake_conn)
    ms_modificar_module.app.dependency_overrides.clear()


@pytest.fixture
def consultar_client(ms_consultar_module, fake_conn):
    yield _build_client(ms_consultar_module, fake_conn)
    ms_consultar_module.app.dependency_overrides.clear()


@pytest.fixture
def borrar_client(ms_borrar_module, fake_conn):
    yield _build_client(ms_borrar_module, fake_conn)
    ms_borrar_module.app.dependency_overrides.clear()


@pytest.fixture
def log_client(ms_log_module, fake_conn):
    yield _build_client(ms_log_module, fake_conn)
    ms_log_module.app.dependency_overrides.clear()
