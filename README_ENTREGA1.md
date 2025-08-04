# 🏨 O11CE - Sistema de Hotel
## Entrega 1: Modelos Base y Estructura del Proyecto

---

## 📋 Resumen de la Entrega 1

Esta entrega incluye la **estructura base del proyecto Django** con los **3 modelos principales** necesarios para el flujo de reserva web cliente:

### ✅ Modelos Creados

| Modelo | App | Descripción | Campos Principales |
|--------|-----|-------------|-------------------|
| `Room` | `app.rooms` | Habitaciones del hotel | `number`, `type`, `status`, `price`, `capacity` |
| `Client` | `app.clients` | Clientes/huéspedes | `first_name`, `last_name`, `email`, `phone`, `dni` |
| `Booking` | `app.bookings` | Reservas del hotel | `client`, `room`, `check_in_date`, `check_out_date`, `status` |

---

## 🏗️ Estructura del Proyecto

```
O11CE/
├── app/
│   ├── rooms/          ← Habitaciones
│   ├── clients/        ← Clientes/Huéspedes  
│   ├── bookings/       ← Reservas
│   ├── administration/ ← Administración
│   ├── cleaning/       ← Limpieza
│   ├── maintenance/    ← Mantenimiento
│   └── users/          ← Usuarios
├── config/             ← Configuración Django
├── core/               ← Core del proyecto
└── manage.py
```

---

## 🧱 Modelos Detallados

### 1. Modelo `Room` (Habitación)

**Campos principales:**
- `number`: Número de habitación (único)
- `type`: Tipo (individual, double, triple, suite, family)
- `status`: Estado (available, occupied, cleaning, maintenance, reserved)
- `price`: Precio por noche
- `capacity`: Capacidad máxima de huéspedes
- `floor`: Piso
- `active`: Si está disponible para reservas

**Métodos útiles:**
- `available_for_booking`: Verifica si está disponible
- `change_status()`: Cambia el estado de la habitación

### 2. Modelo `Client` (Cliente)

**Campos principales:**
- `first_name`, `last_name`: Nombre y apellido
- `email`: Email (único)
- `phone`: Teléfono
- `dni`: Documento de identidad (único)
- `nationality`: Nacionalidad
- `vip`: Si es cliente VIP

**Métodos útiles:**
- `full_name`: Nombre completo
- `get_booking_history()`: Historial de reservas
- `get_active_bookings()`: Reservas activas

### 3. Modelo `Booking` (Reserva)

**Campos principales:**
- `client`: Cliente que reserva (FK)
- `room`: Habitación reservada (FK)
- `check_in_date`, `check_out_date`: Fechas de llegada y salida
- `status`: Estado (pending, confirmed, cancelled, completed)
- `payment_status`: Estado del pago
- `total_price`: Precio total
- `guests_count`: Número de huéspedes

**Métodos útiles:**
- `duration`: Duración en días
- `is_active`: Si la reserva está activa
- `confirm_booking()`: Confirma la reserva
- `cancel_booking()`: Cancela la reserva

---

## 🚀 Instrucciones de Ejecución

### 1. Crear las migraciones
```bash
python manage.py makemigrations
```

### 2. Aplicar las migraciones
```bash
python manage.py migrate
```

### 3. Crear superusuario (opcional)
```bash
python manage.py createsuperuser
```

### 4. Poblar con datos de ejemplo
```bash
python manage.py shell < populate_data.py
```

### 5. Ejecutar el servidor
```bash
python manage.py runserver
```

### 6. Acceder al admin
- URL: `http://localhost:8000/admin/`
- Usar las credenciales del superusuario

---

## 📊 Datos de Ejemplo Creados

El script `populate_data.py` crea:

### Habitaciones (12 habitaciones)
- **Individuales**: 101, 102, 103 ($50-55/noche)
- **Dobles**: 201, 202, 203, 204 ($80-85/noche)
- **Triples**: 301, 302 ($120/noche)
- **Suites**: 401, 402 ($150-160/noche)
- **Familiares**: 501, 502 ($180/noche)

### Clientes (5 clientes)
- Juan Pérez, María González, Carlos López, Ana Martínez, Roberto Fernández
- Todos con emails, teléfonos y DNIs únicos
- Roberto Fernández marcado como VIP

### Reservas (3 reservas de ejemplo)
- Reservas confirmadas, pendientes y con diferentes estados de pago
- Fechas futuras para evitar conflictos

---

## 🔧 Configuración del Admin

Todos los modelos están registrados en el admin de Django con:

- **Listas personalizadas** con campos relevantes
- **Filtros** por estado, tipo, fechas
- **Búsqueda** por nombre, email, número de habitación
- **Acciones** para confirmar/cancelar reservas
- **Campos editables** para cambios rápidos

---

## ✅ Validaciones Implementadas

### Room (Habitación)
- Número único
- Estados válidos
- Precio positivo

### Client (Cliente)
- Email único
- DNI único
- Validación de formato de teléfono
- Validación de formato de DNI

### Booking (Reserva)
- Fechas coherentes (check-out > check-in)
- No reservas para fechas pasadas
- Verificación de disponibilidad de habitación
- Cálculo automático del precio total

---

## 🎯 Próximos Pasos (Entrega 2)

Para la siguiente entrega, implementaremos:

1. **API REST** con Django REST Framework
2. **Endpoints principales**:
   - `GET /api/rooms/available/` - Habitaciones disponibles
   - `POST /api/bookings/create/` - Crear reserva con cliente
   - `POST /api/email/send/` - Envío de emails (opcional)
3. **Validaciones de negocio**
4. **Tests unitarios**
5. **Documentación de API**

---

## 📝 Notas Técnicas

- **Nombres en inglés**: Todos los campos y métodos usan nomenclatura en inglés
- **Comentarios en español**: Documentación y comentarios en español
- **Relaciones**: Foreign Keys bien definidas entre modelos
- **Índices**: Optimización de consultas con índices en campos clave
- **Validaciones**: Validaciones personalizadas en los modelos
- **Métodos útiles**: Métodos helper para operaciones comunes

---

## 🐛 Solución de Problemas

### Error de migraciones
```bash
python manage.py makemigrations --empty app_name
python manage.py makemigrations
```

### Error de importación
Verificar que las apps estén en `INSTALLED_APPS` en `config/settings.py`

### Error de datos
```bash
python manage.py flush  # Limpia la base de datos
python manage.py shell < populate_data.py  # Repuebla
```

---

**🎉 ¡Entrega 1 completada! Los modelos están listos para la implementación de la API.** 