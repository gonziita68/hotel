## Objetivo
Implementar un panel interno MVP por hotel que permita: dashboard con métricas calculables, listado/filtrado de reservas, cambio de estado con reglas simples, listado de habitaciones y clientes; todo filtrado por el hotel activo.

## Hotel Activo (Seguridad y Consistencia)
- Helper `get_hotel_activo(request)`:
  - Si `?hotel=<slug>` existe y es válido → usar ese hotel.
  - Si no, usar hotel por defecto (ej. primero) o redirigir a selector.
- TODAS las consultas filtran por `hotel_activo`:
  - `Booking.objects.filter(hotel=hotel_activo, ...)`
  - `Room.objects.filter(hotel=hotel_activo, ...)`
  - `Client.objects.filter(hotel=hotel_activo, ...)`
- Vistas por ID SIEMPRE validan hotel:
  - `booking_detail`: `get_object_or_404(Booking, id=id, hotel=hotel_activo)`
  - `panel_change_booking_status`: idem.
- Los enlaces del panel preservan filtros activos (`?hotel=...&fecha=...&estado=...`).

## Dashboard (Métricas calculables)
- Métricas por `hotel_activo`:
  - Reservas de hoy (totales).
  - Pendientes hoy.
  - Confirmadas hoy.
  - Ocupación actual (% habitaciones ocupadas vs total del hotel).
  - (Opcional) Reservas del mes.
- UI: tarjetas simples con enlaces rápidos (ver reservas de hoy, ver pendientes).

## Reservas
- `GET /panel/reservas/` (filtros): `?hotel=<slug>&fecha=<yyyy-mm-dd>&estado=<pending|confirmed|cancelled|completed>`.
- `GET /panel/reservas/<id>/`: detalle filtrado por hotel.
- `POST /panel/reservas/<id>/cambiar-estado/`:
  - Validar estado ∈ `STATUS_CHOICES`.
  - Validar transición con matriz simple:
    - `pending → confirmed | cancelled`
    - `confirmed → completed | cancelled`
    - `completed`/`cancelled` → no cambian.

## Habitaciones
- `GET /panel/habitaciones/?hotel=<slug>&type=&status=` listado + filtros.
- Acciones MVP: cambio de `status` simple; CRUD avanzado (crear/editar/borrar) vía admin de Django.

## Clientes
- `GET /panel/clientes/?hotel=<slug>` listado simple por hotel.
- Alta/edición → vía admin en MVP.

## Templates (UI/UX)
- Reutilizar `templates/base.html` para panel.
- Parciales:
  - `panel/partials/hotel_filter.html` (selector de hotel que reenvía con query params).
  - `panel/partials/status_badge.html`.
- Páginas:
  - `panel/dashboard.html`.
  - `panel/bookings_list.html` y `panel/booking_detail.html` (form de cambio de estado).
  - `panel/rooms_list.html`.
  - `panel/clients_list.html`.

## Validación
- Pruebas manuales:
  - Cambiar estado de reserva y verificar reglas.
  - Filtros por hotel/fecha/estado aplicados en listados.
  - Acceso directo a `/panel/reservas/<id>/` con un ID de otro hotel → 404 (o error controlado).
  - Ocupación y métricas de dashboard cambian según `hotel_activo`.

## Implementación (Checklist)
1. Crear `get_hotel_activo(request)` y aplicarlo en todas las vistas `/panel/*`.
2. Extender `bookings_view` con filtros `fecha` y `estado`, preservando query params en enlaces.
3. Cambiar `booking_detail` y `panel_change_booking_status` para filtrar por `hotel_activo` y validar transiciones.
4. Ajustar `rooms_view` y `clients_view` con selector de hotel y filtros básicos.
5. Crear templates del panel (dashboard, bookings, rooms, clients) y parciales (selector hotel, status badge).
6. Verificar métricas del dashboard y enlaces rápidos.
7. Pruebas de aislamiento por hotel y transiciones de estado.

¿Confirmás este plan ajustado para implementar el panel (Paso 3)?