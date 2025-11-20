## Objetivo del Proyecto
- Desarrollar un sistema SaaS para hoteles pequeños y medianos que permita:
- recibir reservas online desde una página web del hotel,
- gestionar habitaciones, reservas y clientes desde un panel interno,
- enviar notificaciones automáticas al cliente,
- reutilizando módulos existentes y manteniendo una arquitectura escalable.

## Alcance y Enfoque
- Prioridad: funcionalidades que aportan al MVP y la evaluación.
- Evitar complejidad innecesaria; dejar la multitenencia avanzada como mejora futura.

## Requisitos Funcionales (MVP)
- RF1 Registrar hotel: modelo Hotel (nombre, slug, email, teléfono, dirección); crear desde admin/panel.
- RF2 Habitaciones por hotel: `Room` con FK a Hotel; CRUD filtrado por hotel.
- RF3 Clientes: datos básicos (nombre, email, teléfono, documento opcional); asegurar relación con Reserva.
- RF4 Reserva online (cliente): flujo de fechas/personas, disponibilidad por hotel, alta de cliente y reserva pendiente/confirmada.
- RF5 CRUD reservas (panel): lista por fecha/estado/hotel; detalle; cambio de estado; asignación de habitación opcional.
- RF6 Notificación al cliente: email automático con datos de reserva y del hotel.
- RF7 Notificación interna al hotel: email al correo del hotel (opcional).
- RF8 Usuario administrador del hotel: rol básico para gestionar su hotel; si complica, usar admin de Django y documentar la integración futura.

## Requisitos No Funcionales
- Web accesible por navegador.
- Multi-hotel a nivel datos: Hotel vinculado en Room, Booking, Client.
- Seguridad básica: login para panel.
- Usabilidad: formularios claros, listados con filtros.
- Escalabilidad conceptual: agregar más hoteles sin cambiar código base.

## Modelo de Datos Mínimo
- Hotel: id, name, slug, email_contact, phone, address.
- Habitacion (Room): id, hotel(FK), code/number, type, capacity, status.
- Cliente (Client): id, full_name, email, phone, document(opcional).
- Reserva (Booking): id, hotel(FK), habitacion(FK opcional por tipo), cliente(FK), check_in, check_out, guests, status, created_at, updated_at.
- UsuarioSistema: id, email, password, role (admin/recepcionista…), hotel(FK opcional), campos existentes.

## Endpoints / Vistas Mínimas
- Cliente público:
- GET /h/<hotel_slug>/reservar/ (formulario fechas + personas)
- POST /h/<hotel_slug>/reservar/ (disponibilidad y opciones)
- POST /h/<hotel_slug>/confirmar-reserva/ (alta cliente + reserva, email)
- Panel del hotel:
- GET /panel/login/
- GET /panel/ (dashboard con reservas de hoy y resumen)
- GET /panel/reservas/ (listado con filtros)
- GET /panel/reservas/<id>/ (detalle)
- POST /panel/reservas/<id>/cambiar-estado/ (transiciones)
- GET /panel/habitaciones/ + CRUD
- GET /panel/clientes/ + listado

## Arquitectura Técnica (ajustada al MVP)
- Multitenencia por columna: `hotel_id` (FK Hotel) en Room, Booking, Client.
- Resolución del hotel:
- Público: por `hotel_slug` en la URL.
- Panel: por el hotel asociado al usuario o filtrado manual en esta versión.
- Base de datos: el sistema está preparado para Postgres vía `DATABASE_URL`; para la demo y pruebas se utiliza `sqlite3` por simplicidad.
- Emails: plantilla simple que incluye datos del hotel; envío automático al crear la reserva.

## Mejoras Futuras (arquitectura SaaS)
- Resolver tenant por dominio/subdominio (ej: hotelx.mi-saas.com).
- Middleware para setear `request.tenant` y filtro automático en todas las consultas.
- Plantillas y branding por hotel; `DEFAULT_FROM_EMAIL` por tenant.
- Integración completa de roles y usuarios propios del SaaS.
- Migración efectiva a Postgres gestionado.

## Plan de Tareas por Fases
- Fase 1 – Alineación de modelos (backend): crear Hotel; agregar `hotel` a Room/Booking/Client; migraciones y datos de prueba.
- Fase 2 – Flujo de reserva SaaS: URLs con `<hotel_slug>`; setear `hotel` al crear reserva; emails con datos del hotel.
- Fase 3 – Panel interno: login; dashboard; listado y detalle de reservas con cambio de estado; CRUD de habitaciones; listado de clientes; filtros por hotel.
- Fase 4 – Documentación: introducción/problema; descripción del sistema; diagrama ER; flujo de reserva; escalado a multi-hotel; capturas; conclusiones y futuro.

## Validación
- Crear dos hoteles, poblar datos, ejecutar reservas cruzadas verificando aislamiento por hotel.
- Comprobar emails, filtros y panel.

¿Confirmás este plan corregido para avanzar con la Fase 1?