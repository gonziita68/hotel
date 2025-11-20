## Objetivo 1: Métricas y Gráficos Basados en Datos Reales
- Fuente de datos disponible:
  - Booking: estados, fechas, total_price, paid_amount, payment_status (`app/bookings/models.py:8–60, 129–186`).
  - Room: estado, precio, tipo, hotel (`app/rooms/models.py:3–58`).
  - Hotel: slug, contacto, is_blocked (`app/administration/models.py:1–17`).
  - EmailLog/ActionLog (`app/core/models.py:34–101`).

### KPIs (definiciones exactas)
- Ocupación hoy = habitaciones ocupadas hoy / habitaciones totales del hotel.
  - Ocupadas hoy: reservas `status=confirmed` con `check_in_date<=hoy` y `check_out_date>=hoy` (distintos `room`).
- Reservas hoy: total, pendientes hoy (`status=pending` solapando hoy), confirmadas hoy (`status=confirmed` solapando hoy).
- Reservas del mes (cantidad): `created_at` dentro del mes o `check_in_date` dentro del mes (definir y usar una sola; recomendamos `check_in_date`).
- ADR (promedio tarifa diaria, opcional si `total_price`): `sum(total_price)/sum(nights)` en período.
- RevPAR diario (opcional si `total_price`): `sum(total_price con check_in=hoy)/total_rooms`.
- Lead time: promedio días entre `created_at` y `check_in_date` en período.
- LOS (length of stay): promedio `duration` (nights) por reserva en período.
- Cancelación y no-show (tasas): `cancelled/total` y `no_show/total` en período.
- Estado de pago: distribución `payment_status` (paid/partial/pending/refunded); deuda total `sum(amount_due)`.
- Email performance: `EmailLog` por `status` (sent/failed) en período; opcional por hotel.
- Actividad panel: `ActionLog` recuento por hotel y por tipo de acción.

### Endpoints JSON (prefijo `/superadmin/api/*`)
- `/kpi/global?desde=&hasta=`: KPIs globales (ocupación promedio, reservas hoy, pendientes, confirmadas, mes, ADR/RevPAR si aplica).
- `/kpi/hotel/<id>?desde=&hasta=`: KPIs del hotel.
- `/series/bookings/daily?days=30&hotel=<id|all>`: serie diaria de reservas (pendientes, confirmadas, canceladas).
- `/series/revenue/daily?days=30&hotel=<id|all>`: serie diaria de revenue (si `total_price`).
- `/distribution/status?hotel=<id|all>&desde=&hasta=`: distribución de estados de reservas.
- `/distribution/payment?hotel=<id|all>&desde=&hasta=`: distribución de `payment_status` y deuda.
- `/top/hotels?metric=bookings|revenue&desde=&hasta=`: ranking hoteles.
- `/audit/email?hotel=<id|all>&desde=&hasta=`: conteo por `EmailLog.status`.
- `/audit/actions?hotel=<id|all>&desde=&hasta=`: actividad por `ActionLog.action`.

### Consultas (ORM precisas)
- Ocupación: `Booking.filter(status='confirmed', check_in_date__lte=today, check_out_date__gte=today).values('room').distinct().count()` y `Room.filter(hotel=h).count()`.
- ADR: `sum(total_price)/sum(duration)` donde `duration=(check_out_date-check_in_date).days` (en model ya existe `duration`).
- Lead time: `Avg(check_in_date - created_at.date())`.
- Series diarias: `annotate(date=TruncDate(field)).values('date').annotate(count=Count('id'))` por estado.
- Cancel/no-show: `Count(status='cancelled')/Count(total)`; `Count(status='no_show')/Count(total)`.
- Payment: `Count(payment_status)` y `Sum(amount_due)` (`amount_due` property; calcular en consulta vía `total_price - paid_amount`).

### Gráficos (frontend)
- Usar Chart.js CDN para: líneas (series diarias), barras (top hoteles), donuts (distribución estados/pagos), tarjetas con KPIs.
- Tooltips y leyendas claras; filtros por rango fecha/hotel que refrescan endpoints.

## Objetivo 2: UI “panel revolucionario modo IA” (sin humo)
- Nuevo layout ya creado: `superadmin/base_superadmin.html` con estilos compartidos del cliente, pero navbar y footer propios.
- Mejoras:
  - Header con selector de hotel y rango de fechas global que persista y refresque KPIs/gráficos.
  - Tarjetas KPI con indicadores de variación (Δ vs ayer/semana) calculadas con endpoints.
  - Dashboard con 4 gráficos: líneas (reservas 30 días), donut (estados), barras (top hoteles), línea/barras (revenue/ADR si aplica).
  - Páginas lista/detalle con componentes reutilizables (client-card) y badges.
- Accesibilidad y responsividad: layouts mobile-first y tablas responsivas.

## Entregables (incremental)
1. Implementar endpoints `/superadmin/api/*` con cálculos exactos y tests manuales de consistencia.
2. Integrar Chart.js en `superadmin/dashboard.html` y wiring de filtros (hotel/rango) a endpoints.
3. Añadir selector global en navbar del `base_superadmin.html` (hotel/rango fechas) con persistencia en query params.
4. Tarjetas KPI con variación vs día anterior/semana.
5. Distribuciones y ranking hoteles.
6. Refinar auditoría (email/actions) con gráficos simples.

## Validación
- Verificar que todos los KPIs y gráficos se basan en datos existentes; si `total_price` falta para algún período, ocultar métricas de revenue.
- Contrastar ocupación y estados con conteos de base.
- Probar filtros y performance de endpoints (paginación/rangos razonables).

¿Confirmás este plan para implementar métricas/gráficos data-driven y mejorar el diseño del panel superadmin?