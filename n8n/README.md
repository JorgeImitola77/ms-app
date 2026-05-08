# n8n — Motor de automatización y RAG

Esta carpeta contiene la configuración del contenedor **n8n** que actúa como
motor de automatización y soporte para el flujo RAG (Retrieval-Augmented
Generation) de ExplorApp.

## Estructura

- `workflows/` — Workflows exportados de n8n en formato JSON. Importar desde
  la UI de n8n (`Settings → Import from File`) o vía la API.
- `credentials/` — Plantillas de credenciales que deben recrearse manualmente
  en cada entorno (no se versionan los secretos reales).
- `data/` — **No versionada**. Volumen persistente local de n8n
  (`/home/node/.n8n` dentro del contenedor).

## Levantar n8n

n8n se inicia junto con el resto de servicios mediante:

```bash
docker compose up -d n8n
```

Una vez arriba, la UI queda disponible en [http://localhost:5678](http://localhost:5678).

## Variables relevantes (ver `.env.example`)

- `N8N_HOST`
- `N8N_PORT`
- `N8N_PROTOCOL`
- `NODE_ENV`
