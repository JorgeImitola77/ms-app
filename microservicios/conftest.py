"""
Conftest raíz para los microservicios.

Hace dos cosas críticas que se ejecutan ANTES de que pytest recolecte tests:

1. Inserta `microservicios/` en sys.path para que `from shared.*` resuelva.
2. Sustituye la ruta hardcoded `/app/uploads` (que solo existe dentro del
   contenedor Docker) por un directorio temporal, parcheando `os.makedirs` y
   `fastapi.staticfiles.StaticFiles.__init__`. Sin esto, los `main.py` de
   ms-crear y ms-consultar fallan al importarse en Windows porque intentan
   crear/leer un directorio absoluto que el usuario de pruebas no puede usar.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

# 1. sys.path -> 'shared' como paquete importable
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# 2. Sustituir /app/uploads por un directorio temporal
_TEST_UPLOAD_DIR = Path(tempfile.gettempdir()) / "ms_app_test_uploads"
_TEST_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

_REDIRECTED = {"/app/uploads", "\\app\\uploads"}

_real_makedirs = os.makedirs


def _patched_makedirs(path, *args, **kwargs):
    if str(path) in _REDIRECTED:
        return _real_makedirs(str(_TEST_UPLOAD_DIR), *args, **kwargs)
    return _real_makedirs(path, *args, **kwargs)


os.makedirs = _patched_makedirs  # type: ignore[assignment]

# StaticFiles valida el directorio en __init__; redirigimos antes de validar.
try:
    from fastapi.staticfiles import StaticFiles  # noqa: E402

    _orig_static_init = StaticFiles.__init__

    def _patched_static_init(self, *args, **kwargs):  # type: ignore[no-redef]
        directory = kwargs.get("directory")
        if directory in _REDIRECTED:
            kwargs["directory"] = str(_TEST_UPLOAD_DIR)
        return _orig_static_init(self, *args, **kwargs)

    StaticFiles.__init__ = _patched_static_init  # type: ignore[assignment]
except Exception:
    # Si FastAPI no está instalado en el momento del collect, los tests que
    # lo necesitan fallarán con un error claro al importar.
    pass

# Variables que algunos módulos leen en import-time.
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("AUTH0_DOMAIN", "test.auth0.com")
os.environ.setdefault("AUTH0_AUDIENCE", "https://test-api")
