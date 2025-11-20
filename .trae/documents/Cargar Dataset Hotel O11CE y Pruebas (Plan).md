## Objetivo
Sembrar datos coherentes (Hotel O11CE + Hotel Demo) relativos a hoy y validar el panel e IA en escenarios normales, vacíos y con fallos.

## Implementación del Seed
- Comando: `app/core/management/commands/seed_o11ce.py`.
- Hoy real: `today = timezone.now().date()`; dataset relativo a `today`.
- Crear Hotel O11CE (contacto/dirección) y 40 Rooms:
  - 101–110 single, 201–215 double, 301–310 triple, 401–405 suite; `status='available'`, `price` por tipo.
- Crear Bookings para O11CE en `[today-19, today+5]` con estados `pending|confirmed|cancelled`:
  - Bloque  ocupación: confirmar 25 rooms solapando hoy (`check_in=today-2`, `check_out=today+2`).
  - Check‑in hoy: 3 reservas (`pending`, `confirmed`, `cancelled`).
- Idempotencia: borrar SOLO `Booking` de O11CE dentro del rango y resetear Rooms O11CE a `available` antes; no tocar otros hoteles.
- Crear Hotel Demo con 5 Rooms y 2–3 Bookings (una confirmada, una cancelada, una pendiente).

## Validaciones Dashboard
- Hotel O11CE: `GET /superadmin/api/dashboard/hotel/<id>?desde=today-19&hasta=today`
  - Esperado: `occupancy_today ≈ 0.625`, `bookings_checkin_today_total = 3`, `reservations_period_count > 0`, distribución con confirmadas predominantes.
- Global: `GET /superadmin/api/dashboard/global?desde=today-19&hasta=today`
  - Suma de O11CE + Demo; verificar agregados vs subconjuntos por hotel.
- Periodo vacío: `GET` con `desde=today+11&hasta=today+15`
  - `reservations_period_count = 0`, series vacía, distribución en cero; `occupancy_today` usa hoy real (documentado).

## Validaciones IA
- Happy path (hotel O11CE): `POST /superadmin/api/ia/analisis/` con `{scope:"hotel",hotel_id,<desde,hasta>}`.
- Rango vacío: mismo endpoint con `desde=today+11,hasta=today+15` → respuesta limitada.
- Scope global: `{scope:"global",<desde,hasta>}`.
- Fallos:
  - IA caído/URL inválida → `503 {"error":"IA no disponible en este momento"}`.
  - Rate limit: 2 POST <15s → `429 {"error":"too_many_requests"}`; >15s OK.
  - Permisos: usuario no superadmin → `403 {"error":"forbidden"}`.

## UI Comprobación
- En `/superadmin/` y `/superadmin/hoteles/<id>/` con filtros del navbar:
  - Ver KPIs coherentes, picos en línea cerca de `today-2 → today+2`, donut con confirmadas.
  - Ejecutar “Analista IA” y ver `answer` + 3 recomendaciones.

## Entregables
- Comando seed con logs claros.
- Resultados de llamadas a endpoints (global y hotel) con capturas.
- Ejemplos IA (normal y error controlado).

¿Confirmás este plan para crear el seed y correr las validaciones ahora?