"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from ninja import NinjaAPI
from app.rooms.api import router as rooms_router
from app.bookings.api import router as bookings_router
from app.core.api import router as core_router
from config.settings import API_TITLE, API_DESCRIPTION, API_VERSION
from django.http import HttpResponse
import json
from enum import Enum
from app.clients.views import clients_api_collection
from app.bookings.views import bookings_api_collection, booking_api_detail, create_booking_api, update_booking_api

# Importar vistas web
from app.core.views import (
    login_view, register_view, logout_view, dashboard_view,
    profile_view, settings_view, bookings_view,
    clients_view, cleaning_view, maintenance_view,
    administration_view, reports_view, dashboard_metrics_api,
    # Vistas del portal de clientes
    client_index_view, client_rooms_view, client_room_detail_view,
    client_booking_view, client_my_bookings_view, client_booking_detail_view,
    client_booking_confirmation_view,
    client_cancel_booking_view, client_profile_view, client_login_view,
    client_register_view, client_logout_view, get_room_availability
)
from app.core.views import client_simulate_payment_view, client_booking_pdf_view
from app.rooms.views import rooms_view, rooms_api_collection, room_api_detail, export_rooms_csv
from app.bookings.views import export_bookings_csv

# Importar vistas de reservas
from app.bookings.views import (
    booking_step1, booking_step2, booking_step3, booking_step4,
    create_booking_final, booking_detail, my_bookings, cancel_booking
)

# Scalar API Reference Implementation
class Layout(Enum):
    MODERN = "modern"
    CLASSIC = "classic"

class SearchHotKey(Enum):
    A = "a"
    B = "b"
    C = "c"
    D = "d"
    E = "e"
    F = "f"
    G = "g"
    H = "h"
    I = "i"
    J = "j"
    K = "k"
    L = "l"
    M = "m"
    N = "n"
    O = "o"
    P = "p"
    Q = "q"
    R = "r"
    S = "s"
    T = "t"
    U = "u"
    V = "v"
    W = "w"
    X = "x"
    Y = "y"
    Z = "z"

scalar_theme = """
/* basic theme */
.light-mode {
  --scalar-color-1: #2a2f45;
  --scalar-color-2: #757575;
  --scalar-color-3: #8e8e8e;
  --scalar-color-accent: #009485;

  --scalar-background-1: #fff;
  --scalar-background-2: #fcfcfc;
  --scalar-background-3: #f8f8f8;
  --scalar-background-accent: #ecf8f6;

  --scalar-border-color: rgba(0, 0, 0, 0.1);
}
.dark-mode {
  --scalar-color-1: rgba(255, 255, 255, 0.9);
  --scalar-color-2: rgba(255, 255, 255, 0.62);
  --scalar-color-3: rgba(255, 255, 255, 0.44);
  --scalar-color-accent: #00ccb8;

  --scalar-background-1: #1f2129;
  --scalar-background-2: #282a35;
  --scalar-background-3: #30323d;
  --scalar-background-accent: #223136;

  --scalar-border-color: rgba(255, 255, 255, 0.1);
}
/* Document Sidebar */
.light-mode .t-doc__sidebar {
  --sidebar-background-1: var(--scalar-background-1);
  --sidebar-item-hover-color: currentColor;
  --sidebar-item-hover-background: var(--scalar-background-2);
  --sidebar-item-active-background: var(--scalar-background-accent);
  --sidebar-border-color: var(--scalar-border-color);
  --sidebar-color-1: var(--scalar-color-1);
  --sidebar-color-2: var(--scalar-color-2);
  --sidebar-color-active: var(--scalar-color-accent);
  --sidebar-search-background: transparent;
  --sidebar-search-border-color: var(--scalar-border-color);
  --sidebar-search--color: var(--scalar-color-3);
}

.dark-mode .sidebar {
  --sidebar-background-1: var(--scalar-background-1);
  --sidebar-item-hover-color: currentColor;
  --sidebar-item-hover-background: var(--scalar-background-2);
  --sidebar-item-active-background: var(--scalar-background-accent);
  --sidebar-border-color: var(--scalar-border-color);
  --sidebar-color-1: var(--scalar-color-1);
  --sidebar-color-2: var(--scalar-color-2);
  --sidebar-color-active: var(--scalar-color-accent);
  --sidebar-search-background: transparent;
  --sidebar-search-border-color: var(--scalar-border-color);
  --sidebar-search--color: var(--scalar-color-3);
}

/* advanced */
.light-mode {
  --scalar-button-1: rgb(49 53 56);
  --scalar-button-1-color: #fff;
  --scalar-button-1-hover: rgb(28 31 33);

  --scalar-color-green: #009485;
  --scalar-color-red: #d52b2a;
  --scalar-color-yellow: #ffaa01;
  --scalar-color-blue: #0a52af;
  --scalar-color-orange: #953800;
  --scalar-color-purple: #8251df;

  --scalar-scrollbar-color: rgba(0, 0, 0, 0.18);
  --scalar-scrollbar-color-active: rgba(0, 0, 0, 0.36);
}
.dark-mode {
  --scalar-button-1: #f6f6f6;
  --scalar-button-1-color: #000;
  --scalar-button-1-hover: #e7e7e7;

  --scalar-color-green: #00ccb8;
  --scalar-color-red: #e5695b;
  --scalar-color-yellow: #ffaa01;
  --scalar-color-blue: #78bffd;
  --scalar-color-orange: #ffa656;
  --scalar-color-purple: #d2a8ff;

  --scalar-scrollbar-color: rgba(255, 255, 255, 0.24);
  --scalar-scrollbar-color-active: rgba(255, 255, 255, 0.48);
}
:root {
  --scalar-radius: 3px;
  --scalar-radius-lg: 6px;
  --scalar-radius-xl: 8px;
}
.scalar-card:nth-of-type(3) {
  display: none;
}"""

def get_scalar_api_reference(
        *,
        openapi_url: str,
        title: str,
        scalar_js_url: str = "https://cdn.jsdelivr.net/npm/@scalar/api-reference",
        scalar_proxy_url: str = "",
        scalar_favicon_url: str = "https://fastapi.tiangolo.com/img/favicon.png",
        scalar_theme: str = scalar_theme,
        layout: Layout = Layout.MODERN,
        show_sidebar: bool = True,
        hide_download_button: bool = False,
        hide_models: bool = False,
        dark_mode: bool = True,
        search_hot_key: SearchHotKey = SearchHotKey.K,
        hidden_clients: list = [],
        servers: list = [],
        default_open_all_tags: bool = False,
) -> HttpResponse:
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <title>{title}</title>
    <!-- needed for adaptive design -->
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="{scalar_favicon_url}">
    <style>
      body {{
        margin: 0;
        padding: 0;
      }}
    </style>
    <style>
    {scalar_theme}
    </style>
    </head>
    <body>
    <noscript>
        Scalar requires Javascript to function. Please enable it to browse the documentation.
    </noscript>
    <script
      id="api-reference"
      data-url="{openapi_url}"
      data-proxy-url="{scalar_proxy_url}"></script>
    <script>
      var configuration = {{
        layout: "{layout.value}",
        showSidebar: {json.dumps(show_sidebar)},
        hideDownloadButton: {json.dumps(hide_download_button)},
        hideModels: {json.dumps(hide_models)},
        darkMode: {json.dumps(dark_mode)},
        searchHotKey: "{search_hot_key.value}",
        hiddenClients: {json.dumps(hidden_clients)},
        servers: {json.dumps(servers)},
        defaultOpenAllTags: {json.dumps(default_open_all_tags)},
      }}

      document.getElementById('api-reference').dataset.configuration =
        JSON.stringify(configuration)
    </script>
    <script src="{scalar_js_url}"></script>
    </body>
    </html>
    """
    return HttpResponse(html)

# Configurar la API de Django Ninja
api = NinjaAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs"  # Habilitar Swagger UI
)

# Agregar los routers de las apps
api.add_router("/", rooms_router)
api.add_router("/", bookings_router)
api.add_router("/", core_router)

# Endpoint de información de la API
@api.get("/info", tags=["Información"])
def api_info(request):
    """
    Información general sobre la API O11CE
    """
    return {
        "name": "O11CE API",
        "version": API_VERSION,
        "description": "API para el sistema de gestión hotelera O11CE",
        "documentation": {
            "swagger": "/api/docs",
            "redoc": "/api/redoc", 
            "scalar": "/api/scalar",
            "openapi_json": "/api/openapi.json"
        },
        "contact": {
            "name": "Equipo O11CE",
            "email": "soporte@o11ce.com",
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        }
    }

# Endpoint para OpenAPI JSON
@api.get("/openapi.json", include_in_schema=False)
def openapi_json(request):
    """
    Especificación OpenAPI en formato JSON
    """
    from django.http import JsonResponse
    return JsonResponse(api.get_openapi_schema())

# Endpoint para ReDoc
@api.get("/redoc", include_in_schema=False)
def redoc_html(request):
    """
    Documentación ReDoc
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{api.title} - ReDoc</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        <style>
            body {{
                margin: 0;
                padding: 0;
            }}
        </style>
    </head>
    <body>
        <redoc spec-url="/api/openapi.json"></redoc>
        <script src="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js"></script>
    </body>
    </html>
    """
    return HttpResponse(html)

# Endpoint para Scalar API Reference
@api.get("/scalar", include_in_schema=False)
def scalar_html(request):
    return get_scalar_api_reference(
        openapi_url="/api/openapi.json",
        title=api.title,
        hide_download_button=False,  # Permitir descarga del OpenAPI spec
        layout=Layout.MODERN,
        dark_mode=True,
        show_sidebar=True,
        hide_models=False,  # Mostrar modelos de datos
        search_hot_key=SearchHotKey.K,
        scalar_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        servers=[
            {
                "url": "http://localhost:8000/api",
                "description": "Servidor de desarrollo"
            },
            {
                "url": "https://api.o11ce.com/api",
                "description": "Servidor de producción"
            }
        ]
    )

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),

    # Endpoints REST de habitaciones para el dashboard
    path("api/rooms/", rooms_api_collection, name="rooms_api_collection"),
    path("api/rooms/<int:room_id>/", room_api_detail, name="room_api_detail"),

    # Endpoints REST de clientes para el dashboard
    path("api/clients/", clients_api_collection, name="clients_api_collection"),

    # Endpoints REST de reservas para el dashboard
    path("api/bookings/", bookings_api_collection, name="bookings_api_collection"),
    path("api/bookings/<int:booking_id>/", booking_api_detail, name="booking_api_detail"),
    
    # Rutas web
    path("", dashboard_view, name="dashboard"),
    path("api/dashboard-metrics/", dashboard_metrics_api, name="dashboard_metrics_api"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("settings/", settings_view, name="settings"),
    
    # Rutas de restablecimiento de contraseña
    path("password_reset/", auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt'
    ), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name="password_reset_complete"),
    
    # Rutas de módulos
    path("rooms/", rooms_view, name="rooms"),
    path("rooms/export/csv/", export_rooms_csv, name="rooms_export_csv"),
    path("bookings/", bookings_view, name="bookings"),
    path("clients/", clients_view, name="clients"),
    path("cleaning/", cleaning_view, name="cleaning"),
    path("maintenance/", maintenance_view, name="maintenance"),
    path("administration/", administration_view, name="administration"),
    path("reports/", reports_view, name="reports"),
    
    # ============================================================================
    # RUTAS DEL PORTAL DE CLIENTES
    # ============================================================================
    path("portal/", client_index_view, name="client_index"),
    path("portal/rooms/", client_rooms_view, name="client_rooms"),
    path("portal/rooms/<int:room_id>/", client_room_detail_view, name="client_room_detail"),
    path("portal/booking/", client_booking_view, name="client_booking"),
    path("portal/booking/<int:room_id>/", client_booking_view, name="client_booking_room"),
    path("portal/room-availability/<int:room_id>/", get_room_availability, name="room_availability_api"),
    path("portal/booking-confirmation/<int:booking_id>/", client_booking_confirmation_view, name="client_booking_confirmation"),
    path("portal/my-bookings/", client_my_bookings_view, name="client_my_bookings"),
    path("portal/my-bookings/<int:booking_id>/", client_booking_detail_view, name="client_booking_detail"),
    path("portal/my-bookings/<int:booking_id>/cancel/", client_cancel_booking_view, name="client_cancel_booking"),
    path("portal/profile/", client_profile_view, name="client_profile"),
    path("portal/login/", client_login_view, name="client_login"),
    path("portal/register/", client_register_view, name="client_register"),
    path("portal/logout/", client_logout_view, name="client_logout"),
    
    # ============================================================================
    # RUTAS DEL PROCESO DE RESERVA MULTI-PASO
    # ============================================================================
    path("booking/step1/", booking_step1, name="booking_step1"),
    path("booking/step2/", booking_step2, name="booking_step2"),
    path("booking/step3/", booking_step3, name="booking_step3"),
    path("booking/step4/", booking_step4, name="booking_step4"),
    path("booking/create/", create_booking_final, name="create_booking_final"),
    path("bookings/<int:booking_id>/", booking_detail, name="booking_detail"),
    path("bookings/<int:booking_id>/cancel/", cancel_booking, name="cancel_booking"),
    path("my-bookings/", my_bookings, name="my_bookings"),
    path('portal/my-bookings/<int:booking_id>/pay/simulate/', client_simulate_payment_view, name='client_simulate_payment'),
    path("bookings/export/csv/", export_bookings_csv, name='export_bookings_csv'),

    # PDF de reserva
    path('portal/my-bookings/<int:booking_id>/pdf/', client_booking_pdf_view, name='client_booking_pdf'),

    # APIs de reservas
    path('api/bookings/', create_booking_api, name='create_booking_api'),
    path('api/bookings/<int:booking_id>/', booking_api_detail, name='booking_api_detail'),
    path('api/bookings/<int:booking_id>/update/', update_booking_api, name='update_booking_api'),

    # Admin booking detail (backend)
    path('admin/bookings/<int:booking_id>/', booking_detail, name='booking_detail'),
]
