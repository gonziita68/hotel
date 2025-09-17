# 🔧 Manual de Administrador - Sistema Hotel O11CE

## 🏨 Guía Completa para Administradores del Sistema

Este manual está dirigido a administradores y personal del hotel que necesitan gestionar el sistema O11CE desde el panel administrativo.

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Acceso Administrativo](#acceso-administrativo)
3. [Panel de Control](#panel-de-control)
4. [Gestión de Habitaciones](#gestión-de-habitaciones)
5. [Gestión de Reservas](#gestión-de-reservas)
6. [Gestión de Clientes](#gestión-de-clientes)
7. [Limpieza y Mantenimiento](#limpieza-y-mantenimiento)
8. [Reportes y Estadísticas](#reportes-y-estadísticas)
9. [Configuración del Sistema](#configuración-del-sistema)
10. [API y Integraciones](#api-y-integraciones)
11. [Mantenimiento del Sistema](#mantenimiento-del-sistema)
12. [Solución de Problemas](#solución-de-problemas)

---

## 🎯 Introducción

El Sistema Hotel O11CE proporciona herramientas administrativas completas para:

- ✅ **Gestionar habitaciones** y su disponibilidad
- ✅ **Supervisar reservas** en tiempo real
- ✅ **Administrar clientes** y su historial
- ✅ **Coordinar limpieza** y mantenimiento
- ✅ **Generar reportes** de ocupación e ingresos
- ✅ **Configurar el sistema** según necesidades del hotel

---

## 🔐 Acceso Administrativo

### Credenciales de Administrador
- **URL Admin**: `http://localhost:8000/admin/`
- **Usuario**: Proporcionado por el equipo técnico
- **Contraseña**: Configurada durante la instalación

### Niveles de Acceso
1. **Super Administrador**: Acceso completo al sistema
2. **Administrador**: Gestión operativa del hotel
3. **Recepcionista**: Operaciones de front desk
4. **Personal de Limpieza**: Gestión de estados de habitaciones
5. **Mantenimiento**: Gestión de incidencias técnicas

### Primer Acceso
1. Ingresa a `/admin/`
2. Usa las credenciales proporcionadas
3. **Cambia la contraseña** inmediatamente
4. Configura tu **perfil de administrador**

---

## 🏠 Panel de Control

### Dashboard Principal
Al acceder verás:

#### Métricas Clave
- **Ocupación actual**: Habitaciones ocupadas vs disponibles
- **Reservas del día**: Check-ins y check-outs programados
- **Ingresos del mes**: Resumen financiero
- **Tareas pendientes**: Limpieza y mantenimiento

#### Accesos Rápidos
- 🛏️ **Habitaciones**: Estado y gestión
- 📅 **Reservas**: Nuevas y modificaciones
- 👥 **Clientes**: Registro y consultas
- 🧹 **Limpieza**: Programación diaria
- 🔧 **Mantenimiento**: Incidencias activas

#### Notificaciones
- **Alertas urgentes**: Problemas críticos
- **Recordatorios**: Tareas programadas
- **Actualizaciones**: Cambios en reservas

---

## 🛏️ Gestión de Habitaciones

### Listado de Habitaciones
**Ruta**: `/habitaciones/`

#### Información Mostrada
- **Número de habitación**
- **Tipo** (Individual, Doble, Suite, etc.)
- **Estado actual** (Libre, Ocupada, Limpieza, Mantenimiento)
- **Capacidad máxima**
- **Precio por noche**
- **Piso de ubicación**

#### Estados de Habitaciones
- 🟢 **Libre**: Disponible para reserva
- 🔴 **Ocupada**: Huésped registrado
- 🟡 **Limpieza**: En proceso de limpieza
- 🟠 **Mantenimiento**: Requiere reparación
- ⚫ **Fuera de servicio**: No disponible

### Crear Nueva Habitación
1. Haz clic en **"Agregar Habitación"**
2. Completa la información:
   - **Número único** de habitación
   - **Tipo de habitación**
   - **Capacidad** (número de personas)
   - **Precio** por noche
   - **Descripción** detallada
   - **Piso** de ubicación
   - **Servicios incluidos**

### Modificar Habitación
1. Selecciona la habitación del listado
2. Haz clic en **"Editar"**
3. Modifica los campos necesarios
4. **Guarda los cambios**

### Cambiar Estado de Habitación
1. Desde el listado, haz clic en el **estado actual**
2. Selecciona el **nuevo estado**
3. Agrega **comentarios** si es necesario
4. **Confirma el cambio**

---

## 📅 Gestión de Reservas

### Panel de Reservas
**Ruta**: `/reservas/`

#### Vista General
- **Calendario mensual** con ocupación
- **Lista de reservas** por fecha
- **Filtros avanzados** de búsqueda
- **Estados de reservas**

#### Información de Reservas
- **Número de reserva** único
- **Cliente** (nombre y contacto)
- **Fechas** de estadía
- **Habitación asignada**
- **Estado** (Confirmada, Pendiente, Cancelada)
- **Precio total**
- **Fecha de creación**

### Crear Reserva Manual
1. Haz clic en **"Nueva Reserva"**
2. **Selecciona fechas** de estadía
3. **Elige habitación** disponible
4. **Busca o crea cliente**:
   - Si existe: selecciona de la lista
   - Si es nuevo: completa formulario
5. **Confirma la reserva**

### Modificar Reserva Existente
1. Busca la reserva por número o cliente
2. Haz clic en **"Editar"**
3. Modifica campos permitidos:
   - Fechas (si hay disponibilidad)
   - Habitación (si hay alternativas)
   - Comentarios especiales
4. **Guarda los cambios**

### Cancelar Reserva
1. Selecciona la reserva
2. Haz clic en **"Cancelar"**
3. **Selecciona motivo** de cancelación
4. **Confirma la cancelación**
5. El sistema enviará **notificación automática** al cliente

### Check-in y Check-out
#### Proceso de Check-in
1. Busca la reserva por número o nombre
2. Verifica **identidad del huésped**
3. Confirma **detalles de la reserva**
4. **Asigna habitación** (si no está asignada)
5. Haz clic en **"Realizar Check-in"**
6. **Entrega llaves** al huésped

#### Proceso de Check-out
1. Busca la reserva activa
2. Verifica **estado de la habitación**
3. **Procesa pagos** pendientes
4. Haz clic en **"Realizar Check-out"**
5. **Cambia estado** de habitación a "Limpieza"

---

## 👥 Gestión de Clientes

### Base de Datos de Clientes
**Ruta**: `/clientes/`

#### Información Almacenada
- **Datos personales**: Nombre, email, teléfono
- **Historial de reservas**: Todas las estadías
- **Preferencias**: Tipo de habitación, servicios
- **Comentarios**: Notas del personal
- **Estado**: Activo, VIP, Bloqueado

### Crear Nuevo Cliente
1. Haz clic en **"Agregar Cliente"**
2. Completa información básica:
   - **Nombre completo**
   - **Email** (único en el sistema)
   - **Teléfono** de contacto
   - **Dirección** (opcional)
3. **Guarda el registro**

### Buscar Clientes
Utiliza los filtros de búsqueda:
- **Por nombre**: Búsqueda parcial
- **Por email**: Búsqueda exacta
- **Por teléfono**: Búsqueda parcial
- **Por fecha de registro**

### Historial del Cliente
Para cada cliente puedes ver:
- **Todas las reservas** realizadas
- **Fechas de estadía**
- **Habitaciones utilizadas**
- **Gastos totales**
- **Comentarios del personal**

---

## 🧹 Limpieza y Mantenimiento

### Gestión de Limpieza
**Ruta**: `/limpieza/`

#### Panel de Limpieza
- **Habitaciones pendientes** de limpieza
- **Personal asignado** por habitación
- **Tiempo estimado** de limpieza
- **Estado de progreso**

#### Asignar Tareas de Limpieza
1. Selecciona **habitaciones** que requieren limpieza
2. **Asigna personal** disponible
3. **Establece prioridad** (Alta, Media, Baja)
4. **Confirma asignación**

#### Completar Limpieza
1. El personal marca **"Limpieza Iniciada"**
2. Al finalizar, marca **"Limpieza Completada"**
3. **Supervisión** verifica calidad
4. **Aprueba** y cambia estado a "Libre"

### Gestión de Mantenimiento
**Ruta**: `/mantenimiento/`

#### Tipos de Mantenimiento
- **Preventivo**: Programado regularmente
- **Correctivo**: Por reportes de problemas
- **Urgente**: Requiere atención inmediata

#### Reportar Incidencia
1. Haz clic en **"Nueva Incidencia"**
2. Selecciona **habitación afectada**
3. **Describe el problema** detalladamente
4. **Asigna prioridad**
5. **Asigna técnico** responsable

#### Seguimiento de Reparaciones
- **Estado actual** de cada incidencia
- **Técnico asignado**
- **Tiempo estimado** de resolución
- **Materiales necesarios**
- **Costo estimado**

---

## 📊 Reportes y Estadísticas

### Dashboard de Reportes
**Ruta**: `/reportes/`

#### Reportes Disponibles
1. **Ocupación Hotelera**
   - Porcentaje de ocupación diario/mensual
   - Comparativas con períodos anteriores
   - Proyecciones de ocupación

2. **Ingresos y Facturación**
   - Ingresos por habitación
   - Ingresos por período
   - Análisis de tarifas promedio

3. **Análisis de Clientes**
   - Clientes frecuentes
   - Origen de reservas
   - Satisfacción del cliente

4. **Operaciones**
   - Tiempos de limpieza
   - Incidencias de mantenimiento
   - Eficiencia del personal

### Generar Reportes Personalizados
1. Selecciona **tipo de reporte**
2. **Define período** de análisis
3. **Aplica filtros** específicos
4. **Genera el reporte**
5. **Exporta** en PDF o Excel

---

## ⚙️ Configuración del Sistema

### Configuraciones Generales
**Ruta**: `/configuracion/`

#### Información del Hotel
- **Nombre del hotel**
- **Dirección completa**
- **Teléfonos de contacto**
- **Email institucional**
- **Políticas generales**

#### Configuración de Reservas
- **Tiempo mínimo** de anticipación
- **Tiempo máximo** de reserva
- **Políticas de cancelación**
- **Depósitos requeridos**

#### Configuración de Emails
- **Servidor SMTP**
- **Plantillas de email**
- **Notificaciones automáticas**
- **Recordatorios**

### Gestión de Usuarios del Sistema
#### Crear Usuario Administrativo
1. Ve a **"Usuarios"** en el panel admin
2. Haz clic en **"Agregar Usuario"**
3. Completa información:
   - **Nombre de usuario**
   - **Email**
   - **Contraseña temporal**
   - **Rol asignado**
4. **Activa la cuenta**

#### Roles y Permisos
- **Super Admin**: Todos los permisos
- **Admin**: Gestión operativa completa
- **Recepcionista**: Reservas y check-in/out
- **Limpieza**: Solo gestión de limpieza
- **Mantenimiento**: Solo incidencias técnicas

---

## 🔌 API y Integraciones

### Documentación de la API
- **Swagger UI**: `/api/docs`
- **ReDoc**: `/api/redoc`
- **Scalar**: `/api/scalar`

#### Endpoints Principales
```
GET /api/habitaciones-disponibles/
POST /api/reservas/crear-con-cliente/
GET /api/reservas/
POST /api/email/send/
```

### Integraciones Externas
#### Sistemas de Pago
- Configuración de pasarelas de pago
- Procesamiento de transacciones
- Reconciliación automática

#### Sistemas de Gestión
- Integración con PMS externos
- Sincronización de datos
- APIs de terceros

---

## 🛠️ Mantenimiento del Sistema

### Tareas Regulares
#### Diarias
- **Backup de base de datos**
- **Verificación de logs**
- **Monitoreo de rendimiento**

#### Semanales
- **Limpieza de archivos temporales**
- **Actualización de estadísticas**
- **Revisión de seguridad**

#### Mensuales
- **Backup completo del sistema**
- **Análisis de rendimiento**
- **Actualización de dependencias**

### Comandos de Mantenimiento
```bash
# Backup de base de datos
python manage.py dumpdata > backup.json

# Limpiar sesiones expiradas
python manage.py clearsessions

# Recolectar archivos estáticos
python manage.py collectstatic

# Verificar integridad del sistema
python manage.py check
```

---

## 🚨 Solución de Problemas

### Problemas Comunes

#### El sistema está lento
1. **Verifica conexión** a internet
2. **Revisa logs** del servidor
3. **Reinicia servicios** si es necesario
4. **Contacta soporte técnico**

#### Error en reservas
1. **Verifica disponibilidad** de habitaciones
2. **Revisa datos del cliente**
3. **Comprueba fechas** seleccionadas
4. **Consulta logs** de errores

#### Problemas de email
1. **Verifica configuración SMTP**
2. **Revisa plantillas** de email
3. **Comprueba conectividad**
4. **Verifica spam/filtros**

### Logs del Sistema
#### Ubicación de Logs
- **Aplicación**: `/logs/app.log`
- **Base de datos**: `/logs/db.log`
- **Email**: `/logs/email.log`
- **Errores**: `/logs/error.log`

#### Interpretar Logs
- **INFO**: Información general
- **WARNING**: Advertencias no críticas
- **ERROR**: Errores que requieren atención
- **CRITICAL**: Errores críticos del sistema

### Contacto de Soporte
#### Soporte Técnico
- **Email**: soporte@o11ce.com
- **Teléfono**: Proporcionado en contrato
- **Horario**: 24/7 para emergencias

#### Información para Soporte
Cuando contactes, incluye:
- **Descripción detallada** del problema
- **Pasos para reproducir** el error
- **Capturas de pantalla**
- **Logs relevantes**
- **Configuración del sistema**

---

## 📚 Recursos Adicionales

### Documentación Técnica
- **Manual de Instalación**: `/docs/INSTALLATION.md`
- **Documentación de API**: `/docs/API_DOCUMENTATION.md`
- **Guía de Desarrollo**: `/docs/DEVELOPMENT.md`

### Capacitación
- **Videos tutoriales**: Disponibles en el portal
- **Sesiones de entrenamiento**: Programables
- **Documentación actualizada**: Revisión mensual

### Actualizaciones
- **Notificaciones automáticas** de nuevas versiones
- **Changelog detallado** de cambios
- **Proceso de actualización** guiado

---

## 📞 Información de Contacto

**Sistema Hotel O11CE - Administración**
- **Soporte Técnico**: soporte@o11ce.com
- **Documentación**: http://localhost:8000/docs/
- **API**: http://localhost:8000/api/docs
- **Versión**: 1.0.0
- **Licencia**: MIT

---

*Este manual se actualiza con cada versión del sistema. Mantente al día con las últimas funcionalidades y mejoras.*

**¡Gestiona tu hotel de manera eficiente con O11CE! 🏨**