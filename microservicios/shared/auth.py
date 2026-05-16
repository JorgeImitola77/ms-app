import os
import json
from urllib.request import urlopen
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

# Variables de entorno que deben estar en tu .env
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
ALGORITHMS = ["RS256"]

security = HTTPBearer()

def validar_token_auth0(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Middleware/Dependencia para FastAPI.
    Intercepta el token JWT, valida su firma con Auth0, verifica su expiración, 
    audience e issuer. Retorna el payload decodificado.
    """
    token = credentials.credentials

    # 1. Obtener la llave pública (JWKS) directamente de tu tenant de Auth0
    try:
        jsonurl = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
    except Exception:
        raise HTTPException(status_code=500, detail="Error conectando con Auth0 para obtener JWKS")

    # 2. Leer la cabecera del token para saber qué llave (kid) usar
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido. Error al decodificar la cabecera.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Emparejar el 'kid' del token con las llaves de Auth0
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header.get("kid"):
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
            break

    if rsa_key:
        try:
            # 4. Decodificar y validar: Firma, Audience, Issuer y Expiración
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f"https://{AUTH0_DOMAIN}/"
            )
            
            # El token es válido. Se retorna el sub (auth0_id) y los claims
            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="El token ha expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTClaimsError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Claims incorrectos. Verifica que el Audience y el Issuer coincidan",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Error genérico al validar el token",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se encontró una llave pública válida (JWKS) para este token",
        headers={"WWW-Authenticate": "Bearer"},
    )