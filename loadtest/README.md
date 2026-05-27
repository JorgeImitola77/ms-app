# Pruebas de carga y rendimiento — card 86e19t0at

Valida el **RNF7**: el backend FastAPI debe soportar peticiones concurrentes sin
degradación visible de latencia ni errores 5xx por timeout.

Herramienta: [Locust](https://locust.io/) (Python, coherente con el stack del
proyecto).

## Escenarios

| Escenario   | Tag        | Endpoint                                                | Carga                            |
|-------------|------------|---------------------------------------------------------|----------------------------------|
| A. Crear    | `crear`    | `POST :8001/api/personas` (multipart)                   | 50 usuarios concurrentes / 1 min |
| B. Consulta | `consulta` | `GET :8003/api/personas/{doc}` (vía nginx LB, escala=3) | 100 usuarios concurrentes / 1 min |
| C. RAG      | `rag`      | `POST :5678/webhook/rag-consulta`                       | 20 usuarios concurrentes / 1 min |

## Prerrequisitos

1. **Levantar el stack** con `consulta` escalado para el escenario B:
   ```powershell
   docker compose up -d --scale consulta=3
   ```

2. **Instalar locust** en el venv de tests del proyecto (se reutiliza
   `.venv-test`):
   ```powershell
   .venv-test\Scripts\python.exe -m pip install -r loadtest\requirements.txt
   ```

3. **Obtener un access token de Auth0** (`client_credentials`). El proyecto
   ya define `AUTH0_CLIENT_SECRET` en `.env`:
   ```powershell
   Get-Content .env | ForEach-Object {
       if ($_ -match '^\s*([^#=]+)=(.*)$') {
           Set-Item -Path "env:$($Matches[1].Trim())" -Value $Matches[2].Trim()
       }
   }
   $env:LOADTEST_TOKEN = (.venv-test\Scripts\python.exe loadtest\get_token.py)
   ```

   > Si tu Auth0 no permite client_credentials sobre la API, puedes pegar
   > manualmente un JWT válido en `LOADTEST_TOKEN`.

4. **(Opcional)** Sembrar `loadtest/data/seed_documentos.txt` con documentos
   reales de tu BD para que el escenario B haga hits 200 (no 404). Por defecto
   trae documentos sintéticos.

## Ejecución

Los escenarios se lanzan desde el menú interactivo de `test.bat`:

```powershell
test.bat
```

Opciones del menú:
- `[6]` Crear     — 50 usuarios x 1m
- `[7]` Consulta  — 100 usuarios x 1m (recordar `--scale consulta=3`)
- `[8]` RAG       — 20 usuarios x 1m
- `[9]` Las 3 cargas secuencialmente

Cada opción genera CSV/HTML en `loadtest/reports/`.

### Modo interactivo (UI web de locust)

Si prefieres la UI:
```powershell
.venv-test\Scripts\locust.exe -f loadtest\locustfile.py --host http://localhost --tags consulta
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
├── data/
│   ├── seed_documentos.txt
│   └── rag_preguntas.txt
└── reports/
    └── REPORTE.md         # plantilla a llenar tras cada corrida
```

> La integración con el menú de `test.bat` (opciones 6-9) lanza locust en modo
> `--headless` con los parámetros del card y vuelca los reportes a
> `loadtest/reports/`. No hay scripts `.bat` propios dentro de `loadtest/`.
