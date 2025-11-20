## Objetivo
Construir endpoints agrupados de dashboard (global/hotel) con KPIs core y gráficos, y un único endpoint IA que interpreta esos mismos datos. Integrar UI con filtros y visualizaciones, manejando errores y límites.

## Definiciones y Reglas
- today = `timezone.now().date()`; todas las métricas “today” usan esta referencia.
- occupancy_today (global): `rooms ocupadas hoy / rooms totales` en todos los hoteles. En hotel: filtro por hotel.
- bookings_checkin_today_total: reservas con `check_in_date = today`.
- reservations_period_count: reservas con `check_in_date ∈ [desde, hasta]`.
- status_distribution: conteos por `status` (pending/confirmed/cancelled) en `check_in_date ∈ [desde, hasta]`.

## Endpoints agrupados
- `GET /superadmin/api/dashboard/global?desde=&hasta=&days=30`
- `GET /superadmin/api/dashboard/hotel/<id>?desde=&hasta=&days=30`
- Query params por defecto: `hasta=today`; `desde=today-30d`; `days=30` (máx 90).
- Respuesta única:
```
{
  meta: {
    version: 1,
    scope: "global"|"hotel",
    hotel_id?: number,
    hotel_name?: string,
    date_range: { from: string, to: string }
  },
  kpis: {
    occupancy_today: number|null,
    bookings_checkin_today_total: number,
    reservations_period_count: number
  },
  series: {
    daily_bookings: [ { date: string, pending: number, confirmed: number, cancelled: number } ]
  },
  distributions: {
    status: { pending: number, confirmed: number, cancelled: number }
  }
}
```
- Errores: `{ "error": "mensaje" }` con códigos: 403 (no superadmin), 404 (hotel inexistente), 400 (fechas/days inválidos).

## Endpoint IA (único)
- `POST /superadmin/api/ia/analisis/`
- Request:
```
{ scope: "global"|"hotel", hotel_id?: number, desde: string, hasta: string, question?: string }
```
- Reglas:
  - scope="hotel" sin `hotel_id` → 400
  - scope="global" → ignorar `hotel_id`
  - hotel inexistente → 404
- Payload a n8n:
```
{
  meta: { version: 1, scope, hotel_name?, date_range: { from, to } },
  kpis: { occupancy_today, bookings_checkin_today_total, reservations_period_count },
  series: { daily_bookings: [...] },
  distributions: { status: {...} },
  question
}
```
- Timeout 5s; en error: log ActionLog (failed) y 503 `{ error: "IA no disponible en este momento" }`. Rate limit IA: 1 req/15s por usuario; sanitize `question`.
- Prompt n8n con guardrails: usar sólo datos del JSON; si la pregunta no aplica, explicar límites y dar 3 recomendaciones basadas en reservas/ocupación/estados.

## UI y Wiring
- `base_superadmin.html`: selector global de hotel y rango (`desde/hasta`) que persiste en query params.
- `superadmin/dashboard.html` y `superadmin/hotel_detail.html`:
  - Tarjetas KPI: `occupancy_today`, `bookings_checkin_today_total`, `reservations_period_count`.
  - Chart.js: línea `daily_bookings` (30 días) y donut `status_distribution`.
  - Card “Analista IA”: alcance global/hotel, fechas, pregunta opcional; render `answer` + 3 recomendaciones; mostrar `{error}` si aplica.

## Orden de ejecución
1. Implementar endpoints dashboard (global/hotel) con validaciones y formato de respuesta.
2. Integrar frontend: fetch de endpoints, tarjetas KPI y gráficos con Chart.js; wiring de filtros.
3. Implementar endpoint IA con timeout, errores, rate limit y logging; UI de card IA.
4. Validar: coherencia de cifras, periodos vacíos → 0 / null; IA fallo seguro.

¿Confirmás este plan para pasar a código inmediato?