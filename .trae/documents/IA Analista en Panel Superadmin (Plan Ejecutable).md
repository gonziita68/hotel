## Objetivo
Integrar un “Analista IA” en el panel superadmin, 100% data‑driven: la IA solo interpreta KPIs/series ya calculados por el backend. Además, elevar el diseño del panel con visualizaciones modernas, filtros globales y UX consistente.

## Contrato Backend ↔ n8n
- Endpoint Django: `POST /superadmin/api/ia/analisis/`
- Request JSON:
  - `scope`: `global` | `hotel`
  - `hotel_id`: entero (requerido si `scope=hotel`)
  - `desde`: `YYYY-MM-DD`
  - `hasta`: `YYYY-MM-DD`
  - `question`: string opcional (si falta, usar prompt por defecto)
- Backend calcula y envía a n8n:
  - `kpis`: `occupancy_today`, `bookings_today`, `pending_today`, `confirmed_today`, `reservations_month_count`, `cancel_rate_period`, `no_show_rate_period`, `lead_time_avg_days`, `los_avg_days`, `payment_distribution` ({pending, partial, paid, refunded}), `amount_due_sum`
  - `series`: `daily_bookings` (últimos N días por estado), `daily_revenue` (opcional si se usa `total_price`), `status_distribution` (periodo)
  - `meta`: `{scope, hotel_name, date_range:{from,to}}`
  - `question`: string
- n8n webhook (env): `N8N_IA_WEBHOOK_URL`
- Respuesta n8n JSON:
  - `answer`: resumen en lenguaje natural
  - `recommendations`: array de 3 recomendaciones concretas
  - `confidence`: 0–1 opcional
- Respuesta Django al frontend: `{answer, recommendations, confidence}`; manejo de errores con `{error}` y código 4xx/5xx.

## Cálculos (ORM exactos)
- Hoy: `today = timezone.now().date()`
- Ocupación hoy por hotel: `occupied = Booking.filter(status='confirmed', check_in_date__lte=today, check_out_date__gte=today).values('room').distinct().count()`; `total_rooms = Room.filter(hotel=h).count()`; `occupancy_today = occupied/total_rooms`
- Reservas hoy: total/pending/confirmed por solape (mismo filtro de fechas)
- Mes: `reservations_month_count = Booking.filter(check_in_date__month=month, check_in_date__year=year).count()`
- Cancel/no-show: en periodo `[desde,hasta]` sobre `Booking.filter(check_in_date__range)`: tasas = `count(status='cancelled')/count(total)` y `count(status='no_show')/count(total)`
- Lead time: `Avg(check_in_date - created_at.date())`
- LOS: `Avg(duration)` (propiedad model)
- Payment: `Count(payment_status)` y `Sum(total_price - paid_amount)`
- Series diarias: `TruncDate(check_in_date)` + `annotate(count=...)` por estado; revenue opcional sumando `total_price` si corresponde.

## Seguridad y límites
- Acceso sólo `is_superuser`/grupo `superadmin`.
- Rate limit simple (p. ej. 1 análisis cada 15s por usuario).
- Tamaño máximo payload n8n (p. ej. 50–200 registros en series).
- Sanitizar `question`; no enviar PII.
- Log de acción en `ActionLog` (tipo: `superadmin_ia_analisis`).

## UI “modo IA” (data‑driven)
- En `superadmin/base_superadmin.html`: selector global de `hotel` y rango `desde/hasta` (persistencia en query params).
- En `superadmin/dashboard.html` y `superadmin/hotel_detail.html`:
  - Card “Analista IA”: select `Global/Hotel actual`, inputs de fecha, textarea opcional “Pregunta”, botón “Analizar”.
  - Loader y bloque “Respuesta IA” con `answer` + lista de `recommendations` (3 items). 
- Visualizaciones (Chart.js CDN):
  - Líneas: reservas diarias últimos 30 días (pendientes/confirmadas/canceladas).
  - Donut: distribución de estados en periodo.
  - Barras: top hoteles por reservas (o revenue si aplica).
  - Tarjetas KPI con variación Δ (vs ayer, vs semana) calculada en backend y enviada a frontend.

## Endpoints Frontend
- `GET /superadmin/api/kpi/global?desde=&hasta=`
- `GET /superadmin/api/kpi/hotel/<id>?desde=&hasta=`
- `GET /superadmin/api/series/bookings/daily?days=30&hotel=<id|all>`
- `GET /superadmin/api/distribution/status?hotel=<id|all>&desde=&hasta=`
- `POST /superadmin/api/ia/analisis/` (feature IA)

## Entregables
1. Implementar endpoints KPI/series/distribución con pruebas básicas de consistencia.
2. Implementar endpoint IA que arma payload y llama a n8n.
3. Integrar Chart.js y wiring con filtros globales.
4. Añadir card “Analista IA” con llamada al endpoint y render de respuesta.
5. Variaciones Δ en KPIs y ranking hoteles.

## Validación
- Comparar métricas vs consultas directas y páginas existentes.
- Testear periodos sin datos (devolver 0 y ocultar revenue si no hay `total_price`).
- Simular distintas preguntas IA y verificar que la respuesta usa solo KPIs/series enviados.

¿Confirmás este plan para avanzar con la implementación data‑driven + IA en el panel superadmin?