## Objetivo
- Integrar el nuevo chat modal con el “agente IA” del backend, usando el workflow n8n existente, asegurando respuestas robustas y manejo de errores.

## Alcance
- Backend: endpoints de chat IA, reutilización del servicio a n8n, rate limiting y control de permisos.
- Frontend: wiring del modal de chat, envío de mensajes, render de respuestas y estados.
- Tests: unitarios del servicio y de los endpoints, más pruebas manuales con curl/Invoke-WebRequest.

## Backend API
- `POST /superadmin/api/ia/chat/` (solo superadmin, CSRF, rate limit 15s/usuario):
  - Body: `{ scope: 'global'|'hotel', hotel_id?: number, desde: 'YYYY-MM-DD', hasta: 'YYYY-MM-DD', question: string }`.
  - Construye contexto agregando KPIs/series/distribuciones vía `get_dashboard_data(scope, hotel, desde, hasta)`.
  - Llama `call_n8n_ia_analyst(payload)` y responde:
    - Éxito síncrono: `{ answer: string, recommendations: string[] }`.
    - Inicio asincrónico n8n: `{ status: 'started' }`.
    - Errores: `429` (rate limit), `403` (permiso), `400` (fechas/scope), `503` (n8n no configurado/caído).
- Opcional (si n8n aporta seguimiento): `GET /superadmin/api/ia/chat/status?job_id=...` para polling de progreso; se implementa si el workflow devuelve un ID.

## Servicio IA (n8n)
- Robustecer `call_n8n_ia_analyst(payload)`:
  - Timeout 10s.
  - Detectar `Content-Type` y parsear JSON; si no JSON, intentar texto.
  - Caso "Workflow was started": retornar `{ status: 'started', answer: null, recommendations: [] }`.
  - Mensajes de error claros ante `URLError` o payload inesperado.

## Seguridad y cumplimiento
- `@login_required` + `is_superadmin` (dev: acceso para autenticado si `DEBUG` true).
- CSRF activo en templates con context processor (ya añadido).
- Validación fechas y rangos (desde ≤ hasta; límite 90 días para parámetros automáticos).
- Sanitizar y validar `hotel_id` existente cuando `scope='hotel'`.

## Frontend Chat
- Reusar el chat modal en `base_superadmin.html`:
  - Enviar `POST /superadmin/api/ia/chat/` con `scope`, `hotel_id` (si se está en detalle hotel), `desde/hasta` del filtro global y `question` del input.
  - Estados:
    - `started`: mostrar “Análisis iniciado” y permitir reintentos tras 15s.
    - `answer`: renderizar respuesta y recomendaciones como mensajes del agente.
    - Errores: mostrar mensajes amigables (403/429/503/400).
  - Mantener conversación en memoria (lista de mensajes del modal) y opcionalmente en `sessionStorage`.

## Pruebas
- Unitarias servicio:
  - `IAServiceNotConfigured` → 503.
  - `URLError` → 503.
  - Respuesta texto “Workflow was started” → `{ status:'started' }`.
  - Respuesta JSON con `answer/recommendations` → éxito.
- Endpoints:
  - `POST /superadmin/api/ia/chat/`: 403 si no superadmin, 429 si se invoca en <15s, 400 si fechas inválidas o falta `hotel_id` en `scope='hotel'`, 200 con `answer` o `status:'started'`.
- Manual/curl:
  - Global:
    - `curl -X POST http://127.0.0.1:8000/superadmin/api/ia/chat/ -H 'Content-Type: application/json' -b <cookie> -d '{"scope":"global","desde":"2025-11-01","hasta":"2025-11-20","question":"Resumen"}'`.
  - Hotel:
    - `curl -X POST http://127.0.0.1:8000/superadmin/api/ia/chat/ -H 'Content-Type: application/json' -b <cookie> -d '{"scope":"hotel","hotel_id":1,"desde":"2025-11-01","hasta":"2025-11-20","question":"Sugerencias"}'`.

## Entregables
- Endpoint nuevo `ia/chat` y wiring del chat modal.
- Servicio IA robusto y documentado en código.
- Pruebas unitarias y guía de pruebas manuales.

## Confirmación
- ¿Avanzo con la implementación según este plan? Una vez confirmado, haré los cambios de backend y frontend, ejecutaré las pruebas y te compartiré la verificación end‑to‑end.