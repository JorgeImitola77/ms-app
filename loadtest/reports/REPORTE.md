# Reporte de pruebas de carga — card 86e19t0at

> Plantilla a completar después de ejecutar cada escenario.
> Llenar las celdas con los valores de `loadtest/reports/<escenario>_stats.csv`
> (fila `Aggregated`) y los HTML generados por locust.

## Entorno

- Fecha de ejecución: _YYYY-MM-DD HH:MM_
- Máquina: _CPU / RAM / SO_
- Versión del stack: _hash de commit_
- Escala de `consulta`: `--scale consulta=3`
- Locust: _versión_
- Notas: _conexión, otros procesos corriendo, etc._

## Escenario A — Crear (50 usuarios concurrentes / 1 min)

| Métrica            | Valor |
|--------------------|-------|
| Requests totales   |       |
| RPS (req/s)        |       |
| Latencia p50 (ms)  |       |
| Latencia p95 (ms)  |       |
| Latencia p99 (ms)  |       |
| Errores 4xx        |       |
| Errores 5xx        |       |
| Failure rate (%)   |       |

Observaciones:
- _¿se mantuvo p95 estable durante toda la corrida?_
- _¿hubo 5xx por timeout?_

## Escenario B — Consulta (100 usuarios concurrentes, escala=3 / 1 min)

| Métrica            | Valor |
|--------------------|-------|
| Requests totales   |       |
| RPS (req/s)        |       |
| Latencia p50 (ms)  |       |
| Latencia p95 (ms)  |       |
| Latencia p99 (ms)  |       |
| Errores 4xx        |       |
| Errores 5xx        |       |
| Failure rate (%)   |       |

Observaciones:
- _¿el round-robin de nginx repartió la carga entre las 3 réplicas?_
  Comprobar con: `docker compose logs consulta | findstr "GET /api/personas"`
- _¿hubo cuello de botella en PostgreSQL?_

## Escenario C — RAG (20 usuarios concurrentes / 1 min)

| Métrica            | Valor |
|--------------------|-------|
| Requests totales   |       |
| RPS (req/s)        |       |
| Latencia p50 (ms)  |       |
| Latencia p95 (ms)  |       |
| Latencia p99 (ms)  |       |
| Errores 4xx        |       |
| Errores 5xx        |       |
| Failure rate (%)   |       |

Observaciones:
- _latencia esperada > Crear/Consulta porque hay llamada a LLM_
- _¿n8n se mantuvo respondiendo o saturó la cola?_

## Conclusión

- [ ] Sin degradación visible en latencia con cargas medias.
- [ ] Sin errores 5xx por timeouts.
- [ ] Reporte anexado.

_Resumen ejecutivo en 2-3 líneas:_
