"""Utilidades compartidas para el manejo uniforme de errores en los microservicios.

Centraliza los mensajes mostrados al cliente y la clasificación de las
excepciones de conexión a la base de datos, de modo que todos los servicios
respondan con el mismo contrato (503 cuando la BD está caída, 500 con un
mensaje amigable cuando ocurre cualquier otro fallo del servidor).
"""

from __future__ import annotations

import asyncpg
from fastapi import HTTPException, status


DB_UNAVAILABLE_MSG = (
    "La base de datos no está disponible en este momento. "
    "Por favor intenta de nuevo en unos minutos."
)

INTERNAL_ERROR_MSG = (
    "Ocurrió un error interno en el servidor. "
    "Por favor intenta de nuevo en unos minutos."
)


_DB_CONNECTION_EXCEPTION_NAMES = {
    "CannotConnectNowError",
    "ConnectionDoesNotExistError",
    "ConnectionFailureError",
    "PostgresConnectionError",
    "InterfaceError",
}


def is_db_connection_error(exc: BaseException) -> bool:
    """Determina si la excepción corresponde a la BD caída o inaccesible."""
    if isinstance(exc, (ConnectionError, OSError, TimeoutError)):
        return True
    if isinstance(exc, asyncpg.PostgresError) and type(exc).__name__ in _DB_CONNECTION_EXCEPTION_NAMES:
        return True
    return type(exc).__name__ in _DB_CONNECTION_EXCEPTION_NAMES


def raise_for_unexpected(exc: BaseException) -> None:
    """Convierte una excepción inesperada en un HTTPException con mensaje amigable.

    - Si es un fallo de conexión a la BD → 503 con `DB_UNAVAILABLE_MSG`.
    - Cualquier otro error → 500 con `INTERNAL_ERROR_MSG`.

    Nunca expone el `str(exc)` original al cliente para no filtrar
    información sensible de la infraestructura.
    """
    if is_db_connection_error(exc):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=DB_UNAVAILABLE_MSG,
        )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=INTERNAL_ERROR_MSG,
    )
