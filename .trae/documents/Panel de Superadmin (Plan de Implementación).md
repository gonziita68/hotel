## Objetivo
Crear un panel para superadmin que permita administrar hoteles (multi‑tenant), usuarios/roles, revisar métricas globales y por hotel, auditar eventos y ejecutar acciones operativas (bloqueo, mantenimiento) manteniendo seguridad y aislamiento.

## Alcance (MVP)
- Gestión de hoteles: alta/edición/bloqueo, ver detalles, dominios/slug y datos de contacto.
- Métricas y reportes: overview global y por hotel (reservas hoy, pendientes, confirmadas, ocupación, reservas del mes opcional, top hoteles por actividad).
- Auditoría: ver `ActionLog` y `EmailLog` filtrados por hotel y fecha.
- Usuarios/roles: listar usuarios, asignar grupo `hotel_admin` y (opcional) vincular a `hotel`.
- Operativa: bloquear hotel (deshabilitar reservas), marcar mantenimiento global en habitaciones del hotel (opcional).

## Roles y Permisos
- Acceso solo para `is_superuser` o grupo `superadmin`.
- Panel del hotel (no superadmin) queda restringido por `hotel_activo`.
- Acciones sensibles (bloqueo hotel, cambios masivos) requieren confirmación.

## Rutas y Controladores
- `GET /superadmin/` dashboard global.
- `GET /superadmin/hoteles/` listado + filtros; `GET /superadmin/hoteles/<id>/` detalle.
- `POST /superadmin/hoteles/<id>/bloquear/` y `POST /superadmin/hoteles/<id>/desbloquear/`.
- `GET /superadmin/auditoria/action-logs/?hotel=<id>&fecha=...` y `GET /superadmin/auditoria/email-logs/?hotel=<id>&fecha=...`.
- `GET /superadmin/usuarios/?hotel=<id>` y `POST /superadmin/usuarios/<id>/asignar-rol/` (hotel_admin, staff, etc.).
- `GET /superadmin/reportes/` export CSV de reservas por hotel, ocupación, actividad.

## Helper y Seguridad
- Decorador/guardia: `@login_required` + verificación `request.user.is_superuser or in_group('superadmin')`; caso contrario 403.
- El panel superadmin NO filtra por `hotel_activo` a menos que se indique; ofrece selector y muestra agregados multi-hotel.
- En vistas de detalle de hotel, todas las consultas se filtran por `hotel=<id>`.

## Templates (UI/UX)
- Base `templates/panel_superadmin/base.html` reutilizando estilos existentes.
- Páginas:
  - `superadmin/dashboard.html`: tarjetas globales + tabla de hoteles (reservas hoy, ocupación, estado).
  - `superadmin/hotels_list.html` y `superadmin/hotel_detail.html`: datos, acciones bloquear/desbloquear, métricas del hotel.
  - `superadmin/audit_actions.html` y `superadmin/audit_emails.html`: tablas con filtros.
  - `superadmin/users_list.html`: usuarios y roles.
  - `superadmin/reports.html`: enlaces de export.
- Parciales: selector de hotel, rango de fechas, badges de estado de hotel (activo/bloqueado).

## Métricas y Consultas
- Globales: conteo reservas hoy (todas), pendientes, confirmadas, ocupación promedio (sum ocupadas/sum totales), actividad por hotel (top N por reservas de la semana).
- Por hotel: mismas métricas filtradas por `hotel`.
- Consultas optimizadas con `annotate` y filtros por fechas en ORM.

## Operaciones de Hotel
- Bloqueo: campo `active` en `Hotel` (o `is_blocked`) que impide nuevas reservas (validación en creación/confirmación), sin afectar reservas existentes.
- Mantenimiento global (opcional): acción que coloca `Room.status='maintenance'` para el hotel, con confirmación.

## Auditoría
- `ActionLog`: listar acciones recientes (filtros por usuario/hotel/fecha).
- `EmailLog`: listar correos enviados, estado, errores; filtros por hotel/fecha.

## Usuarios/Roles
- Vista para asignar grupo `hotel_admin` y vincular usuario ↔ hotel (opcional en MVP).
- Documentar integración futura de RBAC más granular.

## Validación
- Probar accesos: usuarios no superadmin deben recibir 403 en `/superadmin/*`.
- Bloqueo de hotel: intentar crear reserva en hotel bloqueado debe fallar con mensaje controlado.
- Métricas: cambiar filtros/fechas y corroborar resultados.
- Auditoría: verificar que logs corresponden al hotel seleccionado.

## Checklist
1. Middleware/guardia de acceso superadmin.
2. Rutas `/superadmin/*` y controladores básicos (hoteles, auditoría, usuarios, reportes).
3. Campo `Hotel.active` o `is_blocked` y validación en reserva.
4. Templates base y páginas principales.
5. Consultas de métricas globales y por hotel.
6. Acciones operativas (bloquear/desbloquear).
7. Pruebas de seguridad y funcionalidad.

¿Confirmás este plan para implementar el panel de superadmin?