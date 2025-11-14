# Sistema de Reservas Multi-Paso - O11CE Hotel

## Descripción General

El sistema de reservas de O11CE Hotel implementa un proceso de reserva completo en 4 pasos, con filtros inteligentes de habitaciones disponibles y envío automático de emails de confirmación.

## Características Principales

### 🔄 Proceso Multi-Paso
1. **Paso 1**: Selección de fechas y número de personas
2. **Paso 2**: Selección de habitación disponible según filtros
3. **Paso 3**: Datos personales del cliente
4. **Paso 4**: Confirmación y resumen final

### 🏠 Filtros Inteligentes de Habitaciones
- Filtrado por capacidad (número de personas)
- Verificación de disponibilidad en fechas seleccionadas
- Exclusión de habitaciones ya reservadas
- Cálculo automático de precios totales

### 📧 Sistema de Emails
- Envío automático de confirmación al crear reserva
- Plantillas HTML personalizadas
- Logs de envío para seguimiento

### 🎨 Interfaz Moderna
- Diseño responsive con Bootstrap 5
- Indicadores de progreso visual
- Validación en tiempo real
- Animaciones y transiciones suaves

## Estructura del Proyecto

### Vistas (Views)
```
app/bookings/views.py
├── booking_step1()          # Selección de fechas y personas
├── booking_step2()          # Selección de habitación
├── booking_step3()          # Datos personales
├── booking_step4()          # Confirmación final
├── create_booking_final()   # Creación de reserva (AJAX)
├── booking_detail()         # Detalle de reserva
├── my_bookings()           # Lista de reservas del usuario
└── cancel_booking()        # Cancelación de reserva (AJAX)
```

### Templates
```
templates/client/booking/
├── step1.html              # Paso 1: Fechas y personas
├── step2.html              # Paso 2: Selección de habitación
├── step3.html              # Paso 3: Datos personales
├── step4.html              # Paso 4: Confirmación
├── detail.html             # Detalle de reserva
└── my_bookings.html        # Lista de reservas
```

### URLs
```
/booking/step1/             # Inicio del proceso
/booking/step2/             # Selección de habitación
/booking/step3/             # Datos personales
/booking/step4/             # Confirmación
/booking/create/            # Crear reserva (POST)
/bookings/<id>/             # Detalle de reserva
/bookings/<id>/cancel/      # Cancelar reserva (POST)
/my-bookings/               # Mis reservas
```

## Flujo del Proceso de Reserva

### 1. Inicio del Proceso
- Usuario accede a `/booking/step1/`
- Selecciona fechas de llegada y salida
- Especifica número de personas
- Validación de fechas en tiempo real

### 2. Selección de Habitación
- Sistema filtra habitaciones disponibles
- Muestra solo habitaciones que cumplen criterios:
  - Capacidad suficiente
  - Disponible en fechas seleccionadas
  - No reservada por otros clientes
- Calcula precio total automáticamente

### 3. Datos Personales
- Formulario con información del cliente
- Pre-llenado si usuario está autenticado
- Validación de campos requeridos
- Campo opcional para solicitudes especiales

### 4. Confirmación
- Resumen completo de la reserva
- Desglose de precios
- Términos y condiciones
- Botón de confirmación final

### 5. Creación de Reserva
- Proceso AJAX para crear reserva
- Validación final de disponibilidad
- Creación/actualización de cliente
- Envío automático de email
- Redirección a detalle de reserva

### 6. Gestión de Reservas
- Visualización de detalles completos
- Lista de reservas con filtros
- Cancelación de reservas confirmadas
- Envío automático de email de cancelación

## Validaciones Implementadas

### Fechas
- Fecha de llegada debe ser al menos mañana
- Fecha de salida debe ser posterior a llegada
- Mínimo 1 día de anticipación

### Habitaciones
- Verificación de disponibilidad en tiempo real
- Exclusión de reservas superpuestas
- Validación de capacidad vs. número de personas

### Cliente
- Validación de email único
- Verificación de DNI único
- Campos requeridos completos

## Funcionalidad de Cancelación

### Características
- **Cancelación de reservas confirmadas**: Solo se pueden cancelar reservas en estado 'confirmed'
- **Validaciones de seguridad**: Verificación de permisos de usuario
- **Actualización automática de habitación**: La habitación vuelve a estar disponible
- **Email de cancelación**: Envío automático de confirmación de cancelación
- **Interfaz intuitiva**: Botones de cancelación en lista y detalle de reservas

### Proceso de Cancelación
1. **Verificación de permisos**: Solo el propietario de la reserva o staff puede cancelar
2. **Validación de estado**: Solo reservas confirmadas pueden ser canceladas
3. **Actualización de estado**: Cambio a 'cancelled' con timestamp
4. **Liberación de habitación**: La habitación vuelve a estado 'available'
5. **Envío de email**: Confirmación automática al cliente
6. **Feedback al usuario**: Mensaje de éxito y redirección

### Endpoints de Cancelación
```
POST /bookings/<id>/cancel/    # Cancelar reserva específica
```

### Respuesta JSON
```json
{
    "success": true,
    "message": "Reserva cancelada exitosamente",
    "redirect_url": "/my-bookings/"
}
```

## Sistema de Emails

### Configuración
- Servicio de email en `app/core/services.py`
- Plantillas HTML en `templates/emails/`
- Logs de envío para seguimiento

### Tipos de Email
- **Confirmación de reserva**: Enviado automáticamente al crear reserva
- **Reenvío**: Función para reenviar confirmación
- **Cancelación**: Enviado automáticamente al cancelar reserva

## Gestión de Reservas

### Estados de Reserva
- `pending`: Pendiente de confirmación
- `confirmed`: Confirmada
- `cancelled`: Cancelada
- `completed`: Finalizada
- `no_show`: No se presentó

### Estados de Pago
- `pending`: Pendiente de pago
- `paid`: Pagado
- `partial`: Pago parcial
- `refunded`: Reembolsado

## Interfaz de Usuario

### Características de UX
- **Indicadores de progreso**: Muestra el paso actual
- **Navegación intuitiva**: Botones anterior/siguiente
- **Validación en tiempo real**: Feedback inmediato
- **Diseño responsive**: Funciona en móviles y desktop
- **Estados de carga**: Spinners durante procesos

### Elementos Visuales
- **Cards de habitaciones**: Diseño atractivo con información completa
- **Resúmenes**: Información clara y organizada
- **Alertas**: Mensajes de éxito y error
- **Gradientes**: Diseño moderno con colores del hotel

## Datos de Prueba

### Script de Población
```bash
python docs/populate_booking_data.py
```

### Script de Pruebas de Cancelación
```bash
python docs/test_cancellation.py
```

### Usuario de Prueba
- **Username**: `testuser`
- **Password**: `testpass123`

### Datos Incluidos
- 8 habitaciones de diferentes tipos
- 5 clientes de ejemplo
- 5 reservas (pasadas, actuales y futuras)
- 1 usuario de prueba con cliente asociado

## API Endpoints

### Reservas
```
POST /api/reservas/crear-con-cliente/     # Crear reserva con cliente
POST /api/reservas/{id}/reenviar-email/   # Reenviar email
```

### Parámetros de Creación
```json
{
    "nombre": "Juan Pérez",
    "email": "juan@email.com",
    "telefono": "+34 600 123 456",
    "dni": "12345678A",
    "habitacion_id": 1,
    "fecha_inicio": "2024-01-15",
    "fecha_fin": "2024-01-17",
    "solicitudes_especiales": "Vista al jardín"
}
```

## Configuración del Sistema

### Variables de Entorno
```python
# Configuración de email
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu-password'

# Configuración de sesión
SESSION_COOKIE_AGE = 86400  # 24 horas
```

### Configuración de Base de Datos
- SQLite para desarrollo
- PostgreSQL recomendado para producción
- Índices optimizados para consultas de disponibilidad

## Mantenimiento

### Tareas Programadas
- Limpieza de sesiones expiradas
- Verificación de disponibilidad
- Envío de recordatorios (futuro)

### Logs y Monitoreo
- Logs de creación de reservas
- Logs de envío de emails
- Métricas de uso del sistema

## Seguridad

### Medidas Implementadas
- Validación CSRF en todos los formularios
- Sanitización de datos de entrada
- Verificación de permisos de usuario
- Protección contra reservas duplicadas

### Recomendaciones
- Usar HTTPS en producción
- Implementar rate limiting
- Validar datos en frontend y backend
- Mantener dependencias actualizadas

## Próximas Mejoras

### Funcionalidades Planificadas
- [x] Cancelación de reservas
- [ ] Sistema de pagos online
- [ ] Modificación de reservas existentes
- [ ] Sistema de puntos/fidelización
- [ ] Notificaciones push
- [ ] Integración con sistemas externos

### Mejoras Técnicas
- [ ] Cache de consultas de disponibilidad
- [ ] Optimización de consultas de base de datos
- [ ] Tests automatizados
- [ ] Documentación de API completa
- [ ] Dashboard de métricas

## Soporte

### Contacto
- **Email**: soporte@o11ce.com
- **Documentación**: `/docs/`
- **API**: `/api/docs`

### Recursos Adicionales
- [Documentación de Django](https://docs.djangoproject.com/)
- [Bootstrap 5](https://getbootstrap.com/docs/5.3/)
- [Django Ninja](https://django-ninja.rest-framework.com/)

### 🧾 Pago
- Paso adicional de pago integrado después de la confirmación
- Estado de pago inicial: `pending`
- Simulación de pago desde detalle y lista de reservas
- Resultados posibles: `paid` (éxito) y `partial` (pago parcial)

### Endpoints de Pago
```
POST /client/bookings/<id>/simulate-payment/   # Simular pago desde cliente
```
- Cuerpo opcional: `result=partial` para pago parcial; sin cuerpo o cualquier otro valor asume éxito
- Requiere autenticación del cliente propietario de la reserva

### Integración en la UI
- En `templates/client/booking/detail.html`: botones "Simular pago exitoso" y "Simular pago parcial" cuando el pago está `pending`
- En `templates/client/booking/my_bookings.html`: acciones rápidas "Simular pago" y "Pago parcial" para reservas con pago `pending`
