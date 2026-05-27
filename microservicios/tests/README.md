# Tests unitarios de los microservicios

Card ClickUp: **86e19rzwg — Escribir tests unitarios con pytest para microservicios**.

Cubre los modelos Pydantic (RF9) y los endpoints de cada microservicio
(`ms-crear`, `ms-modificar`, `ms-consultar`, `ms-borrar`, `ms-log`).

## Estructura

```
microservicios/
├── conftest.py           ← parchea /app/uploads y AUTH/DB env vars para tests
├── pytest.ini            ← configuración (asyncio_mode=auto, testpaths=tests)
├── .coveragerc           ← coverage solo sobre código de producción
└── tests/
    ├── conftest.py       ← fixtures (clientes TestClient + FakeConnection)
    ├── helpers.py        ← load_service(), FakeConnection, override_auth
    ├── coverage_report.txt
    ├── test_auth.py
    ├── test_models.py                ← 62 tests sobre PersonaCreate/Update/Response
    ├── test_ms_crear.py
    ├── test_ms_modificar.py
    ├── test_ms_consultar.py
    ├── test_ms_borrar.py
    ├── test_ms_log.py
    ├── test_ms_crear_schemas.py      ← schemas locales de cada micro
    └── test_shared_database_orm.py   ← shared/database.py + orm_models.py
```

## Cómo correrlos

Recomendado: un venv aislado para no contaminar las dependencias del proyecto.
**El proyecto requiere Python 3.13** (pydantic-core 2.33 todavía no publica
wheels para 3.14, así que con 3.14 falla la instalación).

```powershell
# desde la raíz del repo (C:\Users\herna\Documents\ms-app)
py -3.13 -m venv .venv-test
.\.venv-test\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install fastapi==0.115.12 pydantic==2.11.1 "pydantic[email]" `
    httpx==0.28.1 pytest==9.0.3 pytest-asyncio pytest-cov `
    python-jose passlib bcrypt python-multipart asyncpg sqlalchemy

cd microservicios
pytest                                         # corre los 120 tests
pytest --cov --cov-report=term-missing         # con coverage en consola
pytest --cov --cov-report=html:coverage_html   # HTML report en coverage_html/
```

En Bash/WSL:

```bash
python3.13 -m venv .venv-test
source .venv-test/bin/activate
pip install -r microservicios/requirements.txt
cd microservicios && pytest --cov --cov-report=term-missing
```

## Resultados actuales

```
TOTAL  391 stmts  20 miss  94.1% cover
120 passed in ~1.2s
```

El objetivo del card era ≥ 70% — superado por ~24 puntos. Las líneas
faltantes son ramas de error genéricas (`except Exception` que solo se
disparan con BD real caída) y el código de Auth0 que necesita un tenant
real para cubrirse 100%.

## Diseño de los tests

### Por qué no usamos SQLite ni Postgres temporal

El card permite cualquiera de las dos opciones. Escogimos **mock-based
testing** porque los handlers reciben la conexión de
`get_db_connection()` (función ad hoc) en vez de inyectarla como
dependencia FastAPI. Cambiar la BD subyacente sin refactorizar requería
parchear la conexión de todos modos; entonces es más limpio
parchearla a un `FakeConnection` que imita los métodos de `asyncpg`
(`fetchrow`, `fetchval`, `fetch`, `execute`, `transaction`, `close`).

Beneficios:
- 120 tests corren en ~1.2 s, sin contenedores ni esperas.
- No depende de que el dev tenga Docker o Postgres local instalados.
- Cobertura ≥ 90% en cada `main.py` de microservicio.

`shared/database.py` (SQLAlchemy async + `get_db`) sí está pensado
para una futura migración a inyección por `Depends(get_db)`; está
cubierto con tests de import y del helper `execute_query_with_error_handling`.

### Cómo se cargan los microservicios

Cada micro vive en un directorio con guion (`ms-crear`), que no es un
identificador Python válido y por lo tanto `import ms-crear.main`
falla. `tests/helpers.py::load_service(name)` hace lo siguiente:

1. Inserta el directorio del servicio en `sys.path`.
2. Limpia `schemas` de `sys.modules` para que cada servicio importe el
   suyo (todos tienen `from schemas import ...` y se pisarían entre sí).
3. Usa `importlib.util.spec_from_file_location` para cargar `main.py`
   como un módulo único llamado p.ej. `ms_crear_main`.
4. Cachea el módulo en `sys.modules` para reusarlo en tests subsiguientes.

### Bypass de autenticación

`shared.auth.validar_token_auth0` se sobrescribe con
`app.dependency_overrides` en `helpers.override_auth(app)`. Devuelve un
payload sintético `{"sub": "auth0|test-user", "email": "test@example.com"}`.
Cada test arranca con un override fresco gracias al fixture
`*_client`, que llama a `app.dependency_overrides.clear()` al cerrar.

### Mock de la BD

`tests/helpers.py::FakeConnection` es un stub que imita la interfaz
mínima de `asyncpg.Connection`:

```python
conn.fetchrow.return_value = {"usuario_id": "...", "email": "..."}
conn.fetchval.side_effect = [1, "uuid-del-usuario"]   # responde en orden
conn.execute.side_effect = asyncpg.UniqueViolationError("duplicate")
```

`transaction()` devuelve un context manager async que es no-op
(`__aenter__` / `__aexit__` sin commit/rollback real).

`helpers.patch_db(module, conn)` reemplaza
`module.get_db_connection` por una corrutina que devuelve `conn`. Se
ejecuta automáticamente desde el fixture `*_client`.

## Cobertura por RF9 (PersonaCreate)

| Constraint | Caso válido | Casos inválidos |
|---|---|---|
| `tipo_documento` Literal | ✅ ambos valores | ✅ Pasaporte, CC, vacío, lowercase |
| `nro_documento` 1-10 dígitos | ✅ 1, 10, 9 dígitos | ✅ 11 dígitos, letras, mixto, vacío, guion |
| `primer_nombre` max 30, sin dígitos | ✅ 30 chars | ✅ 31 chars, con dígitos en cualquier posición |
| `segundo_nombre` (opcional, mismas reglas) | ✅ omitido + con valor | ✅ dígitos, 31 chars |
| `apellidos` max 60, sin dígitos | ✅ 60 chars | ✅ 61 chars, con dígitos |
| `genero` Literal | ✅ los 4 valores | ✅ lowercase, M, Otro, vacío |
| `correo` EmailStr | ✅ 3 formatos comunes | ✅ sin @, con espacios, vacío |
| `celular` 10 dígitos exactos | ✅ 10 dígitos | ✅ 9, 11, con guion, letras, vacío |
| `fecha_nacimiento` date | ✅ ISO 8601 | ✅ DD-MM-YYYY |

## Bugs detectados durante el testing

### ms-log: validación de fecha mal capturada

En `ms-log/main.py`, el bloque que parsea el filtro `fecha`:

```python
try:
    query = ...                         # outer try
    ...
    if fecha:
        try:
            fecha_obj = date.fromisoformat(fecha)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido...")
    ...
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))  # ← se traga el 400
```

El `except Exception` exterior captura la `HTTPException(400)` y la
re-lanza como **500** con detalle `"400: Formato de fecha inválido. Usa
YYYY-MM-DD."`. El test `test_logs_fecha_invalida_se_propaga_como_error`
afirma este comportamiento real. La corrección (en otro card) es añadir
`except HTTPException: raise` **antes** del catch genérico, como ya hacen
los demás microservicios (`ms-borrar`, `ms-consultar`, `ms-modificar`).

### ms-crear: documento duplicado devuelve 400 en vez de 409

El card 86e19rzwg pide explícitamente `409 por duplicado`. El handler
hoy responde con `400` al capturar `asyncpg.UniqueViolationError`. El
test `test_crear_persona_documento_duplicado_devuelve_400` afirma lo
que el código hace hoy. Sugerencia: cambiar el código a
`HTTPException(409, ...)` para alinear con el card y con la convención
REST.
