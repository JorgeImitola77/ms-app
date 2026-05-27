"""
Obtiene un access token de Auth0 (client_credentials) y lo imprime a stdout.

Lee AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET y AUTH0_AUDIENCE
desde el entorno (típicamente cargados desde el .env del proyecto).

Uso (PowerShell):
    $env:LOADTEST_TOKEN = (python loadtest/get_token.py)

Uso (bash):
    export LOADTEST_TOKEN=$(python loadtest/get_token.py)
"""

from __future__ import annotations

import os
import sys

import requests


def main() -> int:
    domain = os.getenv("AUTH0_DOMAIN", "").strip()
    client_id = os.getenv("AUTH0_CLIENT_ID", "").strip()
    client_secret = os.getenv("AUTH0_CLIENT_SECRET", "").strip()
    audience = os.getenv("AUTH0_AUDIENCE", "").strip()

    faltantes = [
        nombre
        for nombre, valor in {
            "AUTH0_DOMAIN": domain,
            "AUTH0_CLIENT_ID": client_id,
            "AUTH0_CLIENT_SECRET": client_secret,
            "AUTH0_AUDIENCE": audience,
        }.items()
        if not valor
    ]
    if faltantes:
        print(
            f"[get_token] Faltan variables de entorno: {', '.join(faltantes)}",
            file=sys.stderr,
        )
        return 2

    url = f"https://{domain}/oauth/token"
    body = {
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": audience,
        "grant_type": "client_credentials",
    }
    resp = requests.post(url, json=body, timeout=15)
    if resp.status_code != 200:
        print(
            f"[get_token] Auth0 devolvió {resp.status_code}: {resp.text}",
            file=sys.stderr,
        )
        return 1

    token = resp.json().get("access_token")
    if not token:
        print("[get_token] La respuesta no contiene access_token", file=sys.stderr)
        return 1

    print(token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
