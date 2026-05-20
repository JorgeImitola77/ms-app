import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Importamos la librería que programaste
from shared.auth import validar_token_auth0

# 1. Creamos una mini-API de prueba
app = FastAPI()

@app.get("/endpoint-protegido")
def endpoint_de_prueba(payload: dict = Depends(validar_token_auth0)):
    return {"mensaje": "Acceso permitido", "usuario": payload}

client = TestClient(app)

# ==========================================
# PRUEBA 1: Sin Token (Criterio de Rechazo)
# ==========================================
def test_sin_token_retorna_error():
    response = client.get("/endpoint-protegido")
    # FastAPI HTTPBearer retorna 403 por defecto cuando no hay cabecera Authorization
    assert response.status_code == 403 

# ==========================================
# PRUEBA 2: Token Inválido (Criterio de Rechazo)
# ==========================================
@patch("shared.auth.urlopen")
def test_token_invalido_retorna_error(mock_urlopen):
    # Simulamos que la conexión a Auth0 funciona para que no lance el error 500
    mock_jwks_response = MagicMock()
    mock_jwks_response.read.return_value = b'{"keys": []}'
    mock_urlopen.return_value = mock_jwks_response

    headers = {"Authorization": "Bearer un_token_totalmente_inventado_y_falso"}
    response = client.get("/endpoint-protegido", headers=headers)
    
    # Ahora sí, el código evaluará el token falso y lanzará el 401
    assert response.status_code == 401
    assert "Token inválido" in response.json()["detail"]

# ==========================================
# PRUEBA 3: Token Válido (Criterio de Éxito con Mock)
# ==========================================
# Usamos @patch para interceptar las funciones de la librería 'jose' y 'urlopen'
@patch("shared.auth.urlopen")
@patch("shared.auth.jwt.get_unverified_header")
@patch("shared.auth.jwt.decode")
def test_token_valido_retorna_exito(mock_decode, mock_get_header, mock_urlopen):
    # A) Simulamos la respuesta de Auth0 enviando llaves públicas falsas
    mock_jwks_response = MagicMock()
    mock_jwks_response.read.return_value = b'{"keys": [{"kid": "llave_ficticia", "kty": "RSA", "use": "sig", "n": "abc", "e": "def"}]}'
    mock_urlopen.return_value = mock_jwks_response

    # B) Simulamos que el token enviado tiene la misma llave en su cabecera
    mock_get_header.return_value = {"kid": "llave_ficticia"}

    # C) Simulamos que la validación matemática de la firma fue exitosa
    mock_decode.return_value = {"sub": "auth0|123456789", "email": "test@explorapp.com"}

    # Disparamos la petición con un token cualquiera (la validación real ya está simulada)
    headers = {"Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.ficticio.firma"}
    response = client.get("/endpoint-protegido", headers=headers)

    # El endpoint debe dejarnos pasar y devolvernos los datos del usuario
    assert response.status_code == 200
    assert response.json()["usuario"]["sub"] == "auth0|123456789"