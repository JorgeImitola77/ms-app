"""
Utilidades compartidas por los tests:

- ``load_service(name)``: importa el ``main.py`` de un microservicio (cuyo
  directorio tiene guiones, p. ej. ``ms-crear``) como módulo independiente.
  No bastaría un ``import`` normal porque los nombres con guion no son
  identificadores Python válidos.
- ``FakeConnection``: stub que imita la interfaz mínima de ``asyncpg.Connection``
  usada por los endpoints (``fetchrow``, ``fetchval``, ``fetch``, ``execute``,
  ``transaction``, ``close``). Cada método es un ``AsyncMock`` para poder
  programar respuestas y verificar llamadas.

Diseño de testing: los endpoints crean conexiones a través de
``get_db_connection()`` (no como dependencia de FastAPI), por lo que la forma
limpia de aislarlos en tests unitarios es monkey-patchear esa función para
que devuelva un ``FakeConnection``. La autenticación sí es dependencia de
FastAPI, así que se sobreescribe con ``app.dependency_overrides``.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest.mock import AsyncMock

ROOT = Path(__file__).resolve().parent.parent  # microservicios/


def load_service(name: str) -> ModuleType:
    """Importa ``microservicios/<name>/main.py`` como módulo único.

    Cada microservicio tiene su propio ``schemas.py``, pero todos lo importan
    con el mismo nombre (``from schemas import ...``). Eso significa que el
    primero gana en ``sys.modules`` y los siguientes obtendrían el schema
    equivocado. Para evitarlo, antes de exec-loadear cada servicio expulsamos
    ``schemas`` del cache y, al terminar, lo volvemos a expulsar para que el
    siguiente ``load_service`` arranque limpio.
    """
    service_dir = ROOT / name
    main_path = service_dir / "main.py"
    if not main_path.exists():
        raise FileNotFoundError(f"No existe {main_path}")

    module_name = f"{name.replace('-', '_')}_main"
    if module_name in sys.modules:
        return sys.modules[module_name]

    # Limpiar el cache de 'schemas' para que main.py importe el suyo, no el
    # del microservicio cargado anteriormente.
    sys.modules.pop("schemas", None)
    sys.path.insert(0, str(service_dir))
    try:
        spec = importlib.util.spec_from_file_location(module_name, main_path)
        assert spec and spec.loader, f"No se pudo crear spec para {main_path}"
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    finally:
        # No dejamos basura para que el próximo servicio cargue su 'schemas'.
        sys.modules.pop("schemas", None)
    return module


class _FakeTransaction:
    """Context manager async que imita ``conn.transaction()`` de asyncpg."""

    async def __aenter__(self) -> "_FakeTransaction":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False  # no se traga excepciones


class FakeConnection:
    """Stub mínimo de ``asyncpg.Connection`` para tests unitarios."""

    def __init__(self) -> None:
        self.fetchrow: AsyncMock = AsyncMock()
        self.fetchval: AsyncMock = AsyncMock()
        self.fetch: AsyncMock = AsyncMock()
        self.execute: AsyncMock = AsyncMock()
        self.close: AsyncMock = AsyncMock()

    def transaction(self) -> _FakeTransaction:
        # asyncpg expone .transaction() como factory síncrona que devuelve un
        # context manager async; replicamos esa forma exacta.
        return _FakeTransaction()


def patch_db(service_module: ModuleType, conn: FakeConnection) -> None:
    """Reemplaza ``service_module.get_db_connection`` por una corrutina que
    devuelve ``conn``. Llamar antes de cada request del TestClient."""

    async def _fake_get_connection() -> Any:
        return conn

    service_module.get_db_connection = _fake_get_connection  # type: ignore[attr-defined]


def override_auth(app, payload: dict[str, Any] | None = None) -> None:
    """Sobreescribe la dependencia ``validar_token_auth0`` para que devuelva
    un payload sintético. Sin esto, FastAPI exigiría un JWT real."""
    from shared.auth import validar_token_auth0

    app.dependency_overrides[validar_token_auth0] = lambda: payload or {
        "sub": "auth0|test-user",
        "email": "test@example.com",
    }
