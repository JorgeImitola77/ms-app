# Configuración de Auth0 - ExplorApp

Este documento detalla la configuración del tenant de Auth0 utilizado para la autenticación Single Sign-On (SSO) y la protección de los microservicios mediante JSON Web Tokens (JWT) en el proyecto ExplorApp.

## 1. Detalles del Tenant
* **Domain:** `dev-i1aenfwhn0il1ty6.us.auth0.com`
* **Región:** US
* **Experiencia de Login:** Universal Login (Activado)

## 2. Configuración de la API (Backend)
Esta API se encarga de validar los tokens JWT enviados desde el frontend hacia los microservicios en FastAPI.
* **Name:** ExplorApp API
* **Identifier (Audience):** `https://api.explorapp`
* **Signing Algorithm:** RS256
* **Token Endpoint Auth Method:** None

## 3. Configuración de la SPA (Frontend)
Aplicación encargada de gestionar la sesión del usuario a través de React.
* **Name:** ExplorApp Web (o ExproApp)
* **Application Type:** Single Page Application (SPA)
* **Client ID:** `iVNnme8tydK9kasEUHCvzlzOuqNEJcow`

### Application URIs configuradas:
Las siguientes URLs están permitidas para el entorno de desarrollo local:
* **Allowed Callback URLs:** `http://localhost:5173`
* **Allowed Logout URLs:** `http://localhost:5173`
* **Allowed Web Origins:** `http://localhost:5173`

## 4. Instrucciones para el equipo de desarrollo
Para conectar tu entorno local a este tenant de Auth0, asegúrate de copiar las siguientes variables de entorno desde el archivo `.env.example` a tu archivo `.env` local:

```env
AUTH0_DOMAIN=dev-i1aenfwhn0il1ty6.us.auth0.com
AUTH0_CLIENT_ID=iVNnme8tydK9kasEUHCvzlzOuqNEJcow
AUTH0_AUDIENCE=[https://api.explorapp](https://api.explorapp)
AUTH0_ALGORITHMS=RS256