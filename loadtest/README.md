# Pruebas de carga y rendimiento — card 86e19t0at

Valida el **RNF7**: el backend FastAPI debe soportar peticiones concurrentes sin
degradación visible de latencia ni errores 5xx por timeout.

Herramienta: [Locust](https://locust.io/) (Python, coherente con el stack del
proyecto).

## Escenarios

| Escenario | Tag        | Endpoint                                             | Carga                            |
|-----------|------------|------------------------------------------------------|----------------------------------|
| A. Crear  | `crear`    | `POST :8001/api/personas` (multipart)                | 50 usuarios concurrentes / 1 min |
| B. Consulta | `consulta` | `GET :8003/api/personas/{doc}` (vía nginx LB, escala=3) | 100 usuarios concurrentes / 1 min |
| C. RAG    | `rag`      | `POST :5678/webhook/rag-consulta`                    | 20 usuarios concurrentes / 1 min |

## Prerrequisitos

1. **Levantar el stack** con `consulta` escalado para el escenario B:
   ```powershell
   docker compose up -d --scale consulta=3
   ```

2. **Instalar locust** en un venv local (no se ejecuta dentro de los
   contenedores para no contaminar las métricas):
   ```powershell
   python -m venv .venv-loadtest
   .venv-loadtest\Scripts\Activate.ps1
   pip install -r loadtest\requirements.txt
   ```

3. **Obtener un access token de Auth0** (client_credentials). El proyecto ya
   define `AUTH0_CLIENT_SECRET` en `.env`:
   ```powershell
   # Carga las variables de .env en la sesión actual (PowerShell)
   Get-Content .env | ForEach-Object {
       if ($_ -match '^\s*([^#=]+)=(.*)$') {
           $env:($Matches[1].Trim()) = $Matches[2].Trim()
       }
   }
   $env:LOADTEST_TOKEN = (python loadtest\get_token.py)
   ```

   > Si la pipeline de tu Auth0 no permite client_credentials sobre la API,
   > puedes pegar manualmente un JWT válido en `LOADTEST_TOKEN`. Para el
   > webhook RAG el token también va en `Authorization: Bearer …`.

4. **(Opcional)** Sembrar `loadtest/data/seed_documentos.txt` con documentos
   reales de tu BD para que el escenario B haga hits 200 (no 404). Por defecto
   trae documentos sintéticos.

## Ejecución

Cada escenario tiene un `.bat` que lanza locust en modo `--headless` y vuelca
resultados a `loadtest/reports/`:

```powershell
loadtest\run-crear.bat
loadtest\run-consulta.bat
loadtest\run-rag.bat
```

Variables opcionales:
- `USERS`        — número de usuarios concurrentes (default por escenario)
- `SPAWN_RATE`   — usuarios por segundo durante el ramp-up
- `RUN_TIME`     — duración (default `1m`)

Ejemplo (ramp-up más rápido):
```powershell
$env:SPAWN_RATE = "50"; loadtest\run-consulta.bat
```

### Modo interactivo (UI web de locust)

Si prefieres la UI:
```powershell
locust -f loadtest\locustfile.py --host http://localhost --tags consulta
```
Luego abre <http://localhost:8089>.

## Métricas capturadas

Locust genera por escenario en `loadtest/reports/`:
- `<escenario>_stats.csv`            — RPS, conteos, latencia media/mediana
- `<escenario>_stats_history.csv`    — serie temporal
- `<escenario>_failures.csv`         — fallos (5xx, timeouts)
- `<escenario>.html`                 — reporte visual

Las columnas relevantes para el criterio de aceptación son
`50%`, `95%`, `99%` (percentiles de latencia en ms), `Requests/s` y `Failure Count`.

## Criterio de aceptación

- [ ] Sin degradación visible en latencia con cargas medias
      (p95 estable a lo largo de la corrida).
- [ ] Sin errores 5xx por timeouts (`Failure Count` en `<escenario>_failures.csv`
      no incluye filas con status 5xx).
- [ ] Reporte de resultados anexado en
      [`loadtest/reports/REPORTE.md`](reports/REPORTE.md).

## Estructura

```
loadtest/
├── README.md
├── requirements.txt
├── locustfile.py          # 3 user classes (Crear / Consultar / Rag) + tags
├── get_token.py           # client_credentials -> access_token
├── run-crear.bat
├── run-consulta.bat
├── run-rag.bat
├── data/
│   ├── seed_documentos.txt
│   └── rag_preguntas.txt
└── reports/
    └── REPORTE.md         # plantilla a llenar tras cada corrida
```
