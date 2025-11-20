## Objetivo
Implementar un panel de superadmin funcional y seguro que administre hoteles (multi‑tenant), muestre métricas globales y por hotel, permita bloqueo/desbloqueo de hoteles, y provea auditoría básica; todo con alcance MVP y sin sobreprometer.

## Alcance (MVP)
- Gestión de hoteles: listado, detalle, bloqueo/desbloqueo (impide nuevas reservas).
- Métricas: reservas hoy (totales/por hotel), pendientes hoy, confirmadas hoy, ocupación actual (% ocupadas vs total habitaciones), (opcional) cantidad de reservas del mes.
- Auditoría básica: listar `ActionLog` y `EmailLog` con filtro por hotel y rango de fechas (los modelos existen en el proyecto).
- Usuarios/roles (MVP): listar usuarios y asignar grupo `hotel_admin`. Vinculación usuario↔hotel se deja como mejora futura.
- Reportes (MVP): export CSV de reservas filtradas por hotel y rango de fechas.

## Seguridad y Aislamiento
- Acceso a `/superadmin/*` sólo para `is_superuser` o grupo `superadmin` (guardia explícita).
- Superadmin puede ver todos los hoteles y sus datos. Aislamiento por ID: 404 si el ID no existe y las vistas de detalle siempre consultan con el hotel correcto.
- El aislamiento entre hoteles (evitar que un admin de hotel vea otro hotel) se aplica en el panel de hotel, no en `/superadmin`.

## Métricas (claras y calculables)
- Ocupación: `ocupadas_hoy / habitaciones_totales_del_hotel`.
- Reservas hoy: total y por estado (pendientes, confirmadas).
- (Opcional) Reservas del mes: conteo de reservas en el mes; no se prometen ingresos salvo que se use `total_price` y se explicite.

## Operaciones sobre hotel
- Campo de bloqueo (ej. `Hotel.is_blocked`): bloquea creación de nuevas reservas en ese hotel; reservas existentes no se alteran.
- Acciones: `POST /superadmin/hoteles/<id>/bloquear/` y `POST /superadmin/hoteles/<id>/desbloquear/` con confirmación y feedback.

## Auditoría
- `ActionLog`: listar acciones clave (accesos, bloqueos) con filtros por hotel/fecha.
- `EmailLog`: correos enviados (estado, errores) con filtros por hotel/fecha.
- La auditoría avanzada queda como mejora futura; en MVP se muestran listas filtrables.

## Usuarios y Roles
- `GET /superadmin/usuarios/`: listado básico.
- `POST /superadmin/usuarios/<id>/asignar-rol/`: asignar grupo `hotel_admin`.
- Vinculación formal usuario↔hotel: documentada como diseño, implementación posterior.

## Reportes CSV (MVP)
- `GET /superadmin/reportes/`: export de reservas filtradas por hotel y rango de fechas.
- Reportes de ocupación/actividad: mejora futura.

## Rutas y Controladores
- `GET /superadmin/`: dashboard global.
- `GET /superadmin/hoteles/`: listado; `GET /superadmin/hoteles/<id>/`: detalle con acciones.
- `POST /superadmin/hoteles/<id>/bloquear/`, `POST /superadmin/hoteles/<id>/desbloquear/`.
- `GET /superadmin/auditoria/action-logs/?hotel=<id>&desde=&hasta=`.
- `GET /superadmin/auditoria/email-logs/?hotel=<id>&desde=&hasta=`.
- `GET /superadmin/usuarios/`, `POST /superadmin/usuarios/<id>/asignar-rol/`.
- `GET /superadmin/reportes/?hotel=<id>&desde=&hasta=`.

## Templates (UI mínima y estable)
- `superadmin/dashboard.html`: tarjetas de métricas + tabla de hoteles con estado.
- `superadmin/hotels_list.html`, `superadmin/hotel_detail.html`: datos y botones bloquear/desbloquear.
- `superadmin/audit_actions.html`, `superadmin/audit_emails.html`: tablas con filtros.
- `superadmin/users_list.html`: usuarios + acción asignar rol.
- `superadmin/reports.html`: formulario de export.
- Parciales: selector de hotel, rango de fechas, badges de estado (activo/bloqueado).

## Validación (pruebas mínimas)
- Acceso: usuario no superadmin → 403 en `/superadmin/*`; superuser → accede.
- Bloqueo: bloquear hotel y confirmar que no se crea nueva reserva en ese hotel; desbloquear y verificar creación normal.
- Métricas: cambiar hotel seleccionado y validar tarjetas; ocupación basada en reservas confirmadas que cruzan hoy.
- Auditoría: generar acción y correo; verificar aparición en listas filtradas por hotel/fecha.
- Reporte: generar CSV de reservas por hotel y rango; contenido correcto.

## Entregables y límites
- Se implementa sólo lo funcional: rutas, guardia, bloqueo, métricas básicas, auditoría mínima y export de reservas.
- Ingresos/monetización, auditoría avanzada, vinculación usuario↔hotel y reportes adicionales quedan como mejoras futuras explícitas.

¿Confirmás este plan ajustado para ejecutar el panel de superadmin dentro del alcance realista del TP?