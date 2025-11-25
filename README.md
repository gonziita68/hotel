# 🏨 Hotel O11CE – Sistema de Gestión Hotelera

Sistema modular para digitalizar la operación de hoteles pequeños y medianos. Incluye backend en Django, API REST y una interfaz web moderna y responsiva que expone todas las funcionalidades clave del negocio.

## Índice

- [Características clave](#características-clave)
- [Requisitos previos](#requisitos-previos)
- [Instalación](#instalación)
- [Ejecución local](#ejecución-local)
- [Estructura de carpetas](#estructura-de-carpetas)
- [Módulos y responsables](#módulos-y-responsables)
- [Uso rápido](#uso-rápido)
- [API REST](#api-rest)
- [Personalización](#personalización)
- [Tecnologías](#tecnologías)
- [Soporte y contacto](#soporte-y-contacto)
- [Licencia](#licencia)

## Características clave

- **Diseño moderno**: interfaz responsiva para desktop, tablet y móvil, con gradientes, animaciones suaves y tipografía Poppins.
- **Autenticación**: login/registro, gestión de perfiles, sesiones persistentes y protección CSRF.
- **Dashboard en vivo**: estadísticas, reservas recientes, estado de habitaciones, alertas de mantenimiento y programación de limpieza.
- **Módulos operativos**: habitaciones, reservas, clientes, limpieza, mantenimiento, administración y reportes.
- **Seguridad**: autenticación requerida en todo el sitio, validaciones de formularios y logout seguro.
- **Escalabilidad**: arquitectura modular con API REST documentada (Swagger/ReDoc) lista para integraciones.

## Requisitos previos

- Python 3.8 o superior
- `pip` y `virtualenv` (recomendado)
- SQLite (incluida para desarrollo) o la base de datos que definas en configuración

Verifica la versión de Python instalada:

```bash
python --version
```

## Instalación

1. Clona el repositorio y entra en el proyecto:
   ```bash
   git clone https://github.com/tuusuario/hotel-o11ce.git
   cd hotel-o11ce
   ```
2. Crea y activa un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Aplica migraciones y crea un superusuario:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

## Ejecución local

Inicia el servidor de desarrollo y accede a `http://localhost:8000`:

```bash
python manage.py runserver
```

## Estructura de carpetas

```text
app/
├── accounts/           # Autenticación, usuarios y roles
├── administration/     # Finanzas básicas, reportes internos
├── bookings/           # Reservas y check-in/out
├── cleaning/           # Programación y seguimiento de limpieza
├── clients/            # Gestión de clientes y perfiles
├── core/               # Configuración y utilidades compartidas
├── maintenance/        # Solicitudes y seguimientos de mantenimiento
├── rooms/              # Gestión de habitaciones
└── superadmin/         # Administración avanzada del sistema
api/index.py            # Punto de entrada de la API Ninja
config/                 # Configuración de proyecto Django
templates/              # Base HTML, dashboard, formularios y vistas públicas
manage.py               # Comandos de administración de Django
requirements.txt        # Dependencias del proyecto
```

## Módulos y responsables

| Módulo (app)      | Rol funcional principal                    | Responsable/Equipo sugerido |
|-------------------|--------------------------------------------|-----------------------------|
| `accounts`        | Usuarios, autenticación y roles            | Seguridad / Plataforma      |
| `rooms`           | Inventario y estados de habitaciones       | Recepción / Mantenimiento   |
| `bookings`        | Reservas, check-in/out, asignaciones       | Recepción                   |
| `clients`         | Datos de huéspedes y preferencias          | Recepción / Marketing       |
| `cleaning`        | Tareas de limpieza y disponibilidad diaria | Housekeeping                |
| `maintenance`     | Incidentes, reparaciones y bloqueos        | Equipo de Mantenimiento     |
| `administration`  | Caja diaria, pagos y reportes básicos      | Administración / Gerencia   |
| `superadmin`      | Configuración avanzada del sistema         | Oficina de TI / Superadmin  |
| `api`             | Endpoints REST y documentación             | Integraciones / Desarrollo  |

## Uso rápido

1. Accede a `http://localhost:8000` y registra un usuario si no tienes credenciales.
2. Usa el dashboard para monitorear reservas, estado de habitaciones y alertas de mantenimiento.
3. Navega por la barra lateral para entrar a los módulos de habitaciones, reservas, clientes, limpieza y reportes.

## API REST

- Documentación: `http://localhost:8000/api/docs`
- Swagger UI: `http://localhost:8000/api/scalar`
- ReDoc: `http://localhost:8000/api/redoc`

## Personalización

Los estilos base están en `templates/base.html` usando variables CSS (colores, tipografías y gradientes). Para añadir nuevas vistas:

1. Crea un template en `templates/` extendiendo `base.html`.
2. Implementa la vista en la app correspondiente.
3. Declara la URL en `config/urls.py`.

## Tecnologías

- **Backend:** Django 5.2 + Django Ninja
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5.3, Font Awesome 6.4
- **Base de datos:** SQLite (desarrollo) / configurable para producción

## Soporte y contacto

- Revisa la documentación y los logs del servidor para diagnósticos rápidos.
- Reporta incidencias o solicita soporte escribiendo a **[contacto@hotel-o11ce.com](mailto:contacto@hotel-o11ce.com)**.
- Para soporte interno, contacta al equipo de desarrollo o al responsable del módulo correspondiente.

## Licencia

Proyecto bajo licencia MIT. Consulta el archivo `LICENSE` para más detalles.
