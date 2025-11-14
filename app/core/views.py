from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from app.clients.forms import ClientRegistrationForm
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q
from django.http import JsonResponse, HttpResponse
from datetime import datetime, timedelta
import locale
from .utils import log_user_action

# Configurar locale para formato de moneda colombiana
try:
    locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'Spanish_Colombia.1252')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
        except locale.Error:
            pass  # Usar formato por defecto si no se puede configurar

# Importar modelos de las apps
from app.rooms.models import Room
from app.bookings.models import Booking
from app.clients.models import Client
try:
    from app.cleaning.models import CleaningTask
except ImportError:
    CleaningTask = None

try:
    from app.maintenance.models import MaintenanceRequest
except ImportError:
    MaintenanceRequest = None

def login_view(request):
    """Vista para el login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if not remember:
                request.session.set_expiry(0)  # Sesión expira al cerrar navegador
            messages.success(request, f'¡Bienvenido, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'login.html')

def register_view(request):
    """Vista para el registro"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.save()
            
            # Autenticar al usuario después del registro
            login(request, user)
            messages.success(request, '¡Cuenta creada exitosamente!')
            return redirect('dashboard')
        else:
            for error in form.errors.values():
                messages.error(request, error[0])
    else:
        form = UserCreationForm()
    
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')

def get_dashboard_metrics():
    """Función para obtener métricas del dashboard de forma optimizada"""
    metrics = {}
    
    # Obtener estadísticas de habitaciones
    try:
        from app.rooms.models import Room as RoomModel
        room_stats = RoomModel.objects.aggregate(
            total=Count('id'),
            available=Count('id', filter=Q(status='available')),
            cleaning=Count('id', filter=Q(status='cleaning')),
            maintenance=Count('id', filter=Q(status='maintenance'))
        )
        
        # Calcular habitaciones ocupadas basándose en reservas activas
        try:
            from app.bookings.models import Booking as BookingModel
            today = datetime.now().date()
            occupied_rooms = BookingModel.objects.filter(
                check_in_date__lte=today,
                check_out_date__gte=today,
                status='confirmed'
            ).values('room').distinct().count()
        except ImportError:
            occupied_rooms = RoomModel.objects.filter(status='occupied').count()
        
        metrics.update({
            'total_rooms': room_stats['total'],
            'available_rooms': room_stats['available'],
            'occupied_rooms': occupied_rooms,
            'cleaning_rooms': room_stats['cleaning'],
            'maintenance_rooms': room_stats['maintenance']
        })
    except ImportError:
        # Datos de ejemplo si no hay modelos
        metrics.update({
            'total_rooms': 50,
            'available_rooms': 35,
            'occupied_rooms': 12,
            'cleaning_rooms': 2,
            'maintenance_rooms': 1
        })
    
    # Obtener estadísticas de reservas e ingresos
    try:
        from app.bookings.models import Booking as BookingModel
        today = datetime.now().date()
        start_of_month = datetime.now().replace(day=1).date()
        
        booking_stats = BookingModel.objects.aggregate(
            active_bookings=Count('id', filter=Q(
                check_in_date__lte=today,
                check_out_date__gte=today,
                status='confirmed'
            )),
            total_revenue=Sum('total_price', filter=Q(
                check_in_date__gte=start_of_month,
                status__in=['confirmed', 'completed']
            ))
        )
        
        metrics.update({
            'active_bookings': booking_stats['active_bookings'] or 0,
            'total_revenue': booking_stats['total_revenue'] or 0,
            'recent_bookings': BookingModel.objects.select_related('client', 'room').order_by('-created_at')[:10]
        })
    except ImportError:
        metrics.update({
            'active_bookings': 15,
            'total_revenue': 25000000,
            'recent_bookings': []
        })
    
    # Obtener estadísticas de clientes
    try:
        from app.clients.models import Client as ClientModel
        metrics['total_clients'] = ClientModel.objects.count()
    except ImportError:
        metrics['total_clients'] = 120
    
    # Obtener alertas de mantenimiento
    try:
        from app.maintenance.models import MaintenanceRequest
        metrics['maintenance_alerts'] = MaintenanceRequest.objects.select_related('room').filter(
            status='pending'
        ).order_by('-priority', '-created_at')[:5]
    except ImportError:
        metrics['maintenance_alerts'] = []
    
    return metrics


@login_required
def dashboard_metrics_api(request):
    """API endpoint para obtener métricas del dashboard en tiempo real"""
    try:
        metrics = get_dashboard_metrics()
        
        # Formatear datos para JSON
        response_data = {
            'total_rooms': metrics['total_rooms'],
            'available_rooms': metrics['available_rooms'],
            'occupied_rooms': metrics['occupied_rooms'],
            'cleaning_rooms': metrics['cleaning_rooms'],
            'maintenance_rooms': metrics['maintenance_rooms'],
            'total_revenue': float(metrics['total_revenue']),
            'active_bookings': metrics['active_bookings'],
            'total_clients': metrics['total_clients'],
            'timestamp': datetime.now().isoformat()
        }
        
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def dashboard_view(request):
    """Vista del dashboard principal"""
    
    # Registrar acceso al dashboard
    log_user_action(request.user, 'dashboard_view', 'Usuario accedió al dashboard', request)
    
    # Handle quick client creation
    if request.method == 'POST' and request.POST.get('action') == 'create_client':
        try:
            if Client:
                client = Client.objects.create(
                    first_name=request.POST.get('first_name'),
                    last_name=request.POST.get('last_name'),
                    email=request.POST.get('email'),
                    phone=request.POST.get('phone', ''),
                    dni=request.POST.get('dni'),
                )
                
                # Registrar creación de cliente
                log_user_action(
                    request.user, 
                    'nuevo_cliente', 
                    f'Cliente creado: {client.first_name} {client.last_name}', 
                    request
                )
                
                return JsonResponse({
                    'success': True,
                    'client_name': f"{client.first_name} {client.last_name}",
                    'client_id': client.id
                })
            else:
                return JsonResponse({'success': False, 'error': 'Client model not available'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Usar la función optimizada para obtener métricas
    context = get_dashboard_metrics()
    
    # Agregar datos adicionales específicos para la vista
    if CleaningTask:
        # Programación de limpieza
        context['cleaning_schedule'] = CleaningTask.objects.select_related('room', 'employee').filter(
            scheduled_date__gte=datetime.now().date()
        ).order_by('scheduled_date')[:10]
    else:
        context['cleaning_schedule'] = []
    
    return render(request, 'dashboard.html', context)

@login_required
def profile_view(request):
    """Vista del perfil de usuario"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        messages.success(request, 'Perfil actualizado exitosamente.')
        return redirect('profile')
    
    return render(request, 'profile.html')

@login_required
def settings_view(request):
    """Vista de configuración"""
    return render(request, 'settings.html')

@login_required
def rooms_view(request):
    """Vista de habitaciones"""
    log_user_action(request.user, 'gestionar_habitaciones', 'Usuario accedió a gestión de habitaciones', request)
    
    if Room:
        rooms = Room.objects.all()
    else:
        rooms = []
    return render(request, 'rooms/list.html', {'rooms': rooms})

@login_required
def bookings_view(request):
    """Vista de reservas"""
    log_user_action(request.user, 'nueva_reserva', 'Usuario accedió a gestión de reservas', request)
    
    if Booking:
        bookings = Booking.objects.select_related('client', 'room').all()
    else:
        bookings = []
    return render(request, 'bookings/list.html', {'bookings': bookings})

@login_required
def clients_view(request):
    """Vista de clientes"""
    if Client:
        clients = Client.objects.all()
    else:
        clients = []
    return render(request, 'clients/list.html', {'clients': clients})

@login_required
def cleaning_view(request):
    """Vista de limpieza"""
    if CleaningTask:
        tasks = CleaningTask.objects.select_related('room', 'employee').all()
    else:
        tasks = []
    return render(request, 'cleaning/list.html', {'tasks': tasks})

@login_required
def maintenance_view(request):
    """Vista de mantenimiento"""
    if MaintenanceRequest:
        requests = MaintenanceRequest.objects.select_related('room').all()
    else:
        requests = []
    return render(request, 'maintenance/list.html', {'requests': requests})

@login_required
def administration_view(request):
    """Vista de administración"""
    return render(request, 'administration/dashboard.html')

@login_required
def reports_view(request):
    """Vista de reportes"""
    log_user_action(request.user, 'ver_reportes', 'Usuario accedió a reportes', request)
    return render(request, 'reports/dashboard.html')

# ============================================================================
# VISTAS DEL PORTAL DE CLIENTES
# ============================================================================

def client_index_view(request):
    """Vista principal del portal de clientes (pública)"""
    if Room:
        # Habitaciones disponibles para mostrar
        available_rooms = Room.objects.filter(
            status='available',
            active=True
        ).order_by('price')[:6]
        
        # Habitaciones destacadas
        featured_rooms = Room.objects.filter(
            active=True
        ).order_by('?')[:3]  # Aleatorio
    else:
        available_rooms = []
        featured_rooms = []
    
    context = {
        'available_rooms': available_rooms,
        'featured_rooms': featured_rooms,
    }
    
    return render(request, 'client/index.html', context)

def client_rooms_view(request):
    """Vista de habitaciones disponibles para clientes"""
    if Room:
        # Obtener todas las habitaciones activas por defecto
        rooms = Room.objects.filter(active=True).order_by('number')
        
        # Aplicar filtros solo si se proporcionan
        room_type = request.GET.get('type', '').strip()
        min_price = request.GET.get('min_price', '').strip()
        max_price = request.GET.get('max_price', '').strip()
        guests = request.GET.get('guests', '').strip()
        status_filter = request.GET.get('status', '').strip()
        
        # Filtro por tipo de habitación
        if room_type:
            rooms = rooms.filter(type=room_type)
            
        # Filtro por precio mínimo
        if min_price:
            try:
                min_price_val = float(min_price)
                if min_price_val >= 0:
                    rooms = rooms.filter(price__gte=min_price_val)
            except (ValueError, TypeError):
                pass
                
        # Filtro por precio máximo
        if max_price:
            try:
                max_price_val = float(max_price)
                if max_price_val >= 0:
                    rooms = rooms.filter(price__lte=max_price_val)
            except (ValueError, TypeError):
                pass
                
        # Filtro por capacidad de huéspedes
        if guests:
            try:
                guests_val = int(guests)
                if guests_val > 0:
                    rooms = rooms.filter(capacity__gte=guests_val)
            except (ValueError, TypeError):
                pass
                
        # Filtro por estado (opcional). Si no se especifica, mostrar solo disponibles
        if status_filter:
            rooms = rooms.filter(status=status_filter)
        else:
            rooms = rooms.filter(status='available')
            
        # Obtener estadísticas para mostrar
        total_rooms = rooms.count()
        available_rooms = rooms.filter(status='available').count()
        
    else:
        rooms = Room.objects.none()
        total_rooms = 0
        available_rooms = 0
    
    context = {
        'rooms': rooms,
        'room_types': Room.TYPE_CHOICES if Room else [],
        'status_choices': Room.STATUS_CHOICES if Room else [],
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'current_filters': {
            'type': room_type,
            'min_price': min_price,
            'max_price': max_price,
            'guests': guests,
            'status': status_filter,
        }
    }
    
    return render(request, 'client/rooms.html', context)

def client_room_detail_view(request, room_id):
    """Vista detallada de una habitación"""
    if Room:
        try:
            room = Room.objects.get(id=room_id, active=True)
        except Room.DoesNotExist:
            messages.error(request, 'Habitación no encontrada.')
            return redirect('client_rooms')
    else:
        room = None
        messages.error(request, 'Sistema de habitaciones no disponible.')
        return redirect('client_rooms')
    
    context = {
        'room': room,
    }
    
    return render(request, 'client/room_detail.html', context)

def client_booking_view(request, room_id=None):
    """Vista para crear una reserva"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para hacer una reserva.')
        return redirect('client_login')
    
    if room_id:
        try:
            room = Room.objects.get(id=room_id, active=True)
            if not room.available_for_booking:
                messages.error(request, 'Esta habitación no está disponible para reservas.')
                return redirect('client_rooms')
        except Room.DoesNotExist:
            messages.error(request, 'Habitación no encontrada.')
            return redirect('client_rooms')
    else:
        room = None
    
    if request.method == 'POST':
        # Procesar la reserva
        room_id_post = request.POST.get('room') or room_id
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        guests_count = request.POST.get('guests_count')
        special_requests = request.POST.get('special_requests', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        
        if room_id_post and check_in and check_out and guests_count:
            try:
                # Obtener la habitación si no está definida
                if not room:
                    room = Room.objects.get(id=room_id_post, active=True)
                
                # Validar capacidad
                if int(guests_count) > room.capacity:
                    messages.error(request, f'La habitación solo tiene capacidad para {room.capacity} personas.')
                    return render(request, 'client/booking.html', {
                        'room': room,
                        'available_rooms': Room.objects.filter(active=True, status='available'),
                    })
                
                # Validar fechas
                from datetime import datetime
                check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
                check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
                
                if check_in_date >= check_out_date:
                    messages.error(request, 'La fecha de salida debe ser posterior a la fecha de entrada.')
                    return render(request, 'client/booking.html', {
                        'room': room,
                        'available_rooms': Room.objects.filter(active=True, status='available'),
                    })
                
                # Validar que las fechas no sean en el pasado
                from datetime import date
                today = date.today()
                if check_in_date < today:
                    messages.error(request, 'La fecha de entrada no puede ser en el pasado.')
                    return render(request, 'client/booking.html', {
                        'room': room,
                        'available_rooms': Room.objects.filter(active=True, status='available'),
                    })
                
                # Validar disponibilidad de la habitación en las fechas seleccionadas
                overlapping_bookings = Booking.objects.filter(
                    room=room,
                    status__in=['confirmed', 'pending'],
                    check_in_date__lt=check_out_date,
                    check_out_date__gt=check_in_date
                )
                
                if overlapping_bookings.exists():
                    messages.error(request, 'La habitación no está disponible en las fechas seleccionadas. Por favor elige otras fechas.')
                    return render(request, 'client/booking.html', {
                        'room': room,
                        'available_rooms': Room.objects.filter(active=True, status='available'),
                    })
                
                # Obtener o crear el cliente
                if hasattr(request.user, 'client'):
                    client = request.user.client
                    # Actualizar información de contacto si se proporciona
                    if phone:
                        client.phone = phone
                    if email:
                        client.email = email
                    client.save()
                else:
                    # Crear perfil de cliente si no existe
                    import random
                    client_email = email or request.user.email
                    if not client_email or Client.objects.filter(email=client_email).exists():
                        client_email = f'{request.user.username}_{random.randint(1000, 9999)}@hotel.com'
                    
                    client = Client.objects.create(
                        user=request.user,
                        first_name=request.user.first_name or request.user.username,
                        last_name=request.user.last_name or 'Usuario',
                        email=client_email,
                        dni=f'{random.randint(10000000, 99999999)}',
                        phone=phone or f'+54911{random.randint(1000000, 9999999)}'
                    )
                
                # Calcular precio total
                nights = (check_out_date - check_in_date).days
                total_price = room.price * nights
                
                # Crear la reserva
                booking = Booking.objects.create(
                    client=client,
                    room=room,
                    check_in_date=check_in_date,
                    check_out_date=check_out_date,
                    guests_count=int(guests_count),
                    special_requests=special_requests,
                    total_price=total_price,
                    status='confirmed'
                )
                
                # Enviar email de confirmación
                try:
                    from .services import EmailService
                    email_result = EmailService.send_booking_confirmation(booking.id)
                    if email_result.get('success'):
                        messages.success(request, f'¡Reserva #{booking.id} creada exitosamente! Se ha enviado una confirmación a tu email.')
                    else:
                        messages.success(request, f'¡Reserva #{booking.id} creada exitosamente! (El email de confirmación no pudo ser enviado)')
                except Exception as email_error:
                    messages.success(request, f'¡Reserva #{booking.id} creada exitosamente! (Error al enviar email: {str(email_error)})')
                
                return redirect('client_booking_confirmation', booking_id=booking.id)
                    
            except ValidationError as e:
                messages.error(request, f'Error de validación: {str(e)}')
            except Exception as e:
                messages.error(request, f'Error al crear la reserva: {str(e)}')
        else:
            messages.error(request, 'Por favor completa todos los campos requeridos.')
    
    # Obtener fechas mínimas para el formulario
    from datetime import date, timedelta
    today = date.today()
    min_checkout = today + timedelta(days=1)
    
    context = {
        'room': room,
        'available_rooms': Room.objects.filter(active=True, status='available'),
        'today': today.isoformat(),
        'min_checkout': min_checkout.isoformat(),
    }
    
    return render(request, 'client/booking.html', context)

def get_room_availability(request, room_id):
    """API para obtener disponibilidad de una habitación por fechas"""
    if not Room:
        return JsonResponse({'error': 'Sistema de habitaciones no disponible'}, status=500)
    
    try:
        room = Room.objects.get(id=room_id, active=True)
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Habitación no encontrada'}, status=404)
    
    # Obtener parámetros de fecha (próximos 60 días por defecto)
    from datetime import date, timedelta
    import json
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)
    else:
        start_date = date.today()
        end_date = start_date + timedelta(days=60)
    
    # Obtener reservas que afectan este período
    if Booking:
        bookings = Booking.objects.filter(
            room=room,
            status__in=['confirmed', 'pending'],
            check_in_date__lte=end_date,
            check_out_date__gt=start_date
        ).values('check_in_date', 'check_out_date', 'status')
    else:
        bookings = []
    
    # Crear diccionario de disponibilidad
    availability = {}
    current_date = start_date
    
    while current_date <= end_date:
        availability[current_date.isoformat()] = {
            'available': True,
            'status': 'available',
            'price': float(room.price)
        }
        current_date += timedelta(days=1)
    
    # Marcar días ocupados
    for booking in bookings:
        booking_start = booking['check_in_date']
        booking_end = booking['check_out_date']
        
        current_date = max(booking_start, start_date)
        end_booking = min(booking_end, end_date + timedelta(days=1))
        
        while current_date < end_booking:
            if current_date.isoformat() in availability:
                availability[current_date.isoformat()] = {
                    'available': False,
                    'status': 'occupied',
                    'price': float(room.price)
                }
            current_date += timedelta(days=1)
    
    return JsonResponse({
        'room_id': room.id,
        'room_number': room.number,
        'room_type': room.get_type_display(),
        'availability': availability,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat()
    })

def client_booking_confirmation_view(request, booking_id):
    """Vista de confirmación de reserva"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para ver esta página.')
        return redirect('client_login')
    
    try:
        # Obtener la reserva
        booking = Booking.objects.get(id=booking_id)
        
        # Verificar que la reserva pertenece al usuario actual
        if booking.client.user != request.user:
            messages.error(request, 'No tienes permiso para ver esta reserva.')
            return redirect('client_rooms')
        
        context = {
            'booking': booking,
            'room': booking.room,
            'client': booking.client,
        }
        
        return render(request, 'client/booking_confirmation.html', context)
        
    except Booking.DoesNotExist:
        messages.error(request, 'Reserva no encontrada.')
        return redirect('client_rooms')

def client_my_bookings_view(request):
    """Vista de las reservas del cliente"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para ver tus reservas.')
        return redirect('client_login')
    
    if Booking and Client:
        # Verificar si el usuario tiene un perfil de cliente
        try:
            client = Client.objects.get(user=request.user)
        except Client.DoesNotExist:
            # Crear perfil de cliente automáticamente
            import random
            email = request.user.email
            if not email or Client.objects.filter(email=email).exists():
                email = f'{request.user.username}_{random.randint(1000, 9999)}@hotel.com'
            
            client = Client.objects.create(
                user=request.user,
                first_name=request.user.first_name or request.user.username,
                last_name=request.user.last_name or 'Usuario',
                email=email,
                dni=f'{random.randint(10000000, 99999999)}',  # DNI temporal
                phone=f'+54911{random.randint(1000000, 9999999)}'  # Teléfono temporal
            )
            messages.info(request, 'Se ha creado tu perfil de cliente automáticamente.')
        
        # Obtener reservas del cliente actual
        bookings = Booking.objects.filter(
            client=client
        ).select_related('room').order_by('-created_at')
    else:
        bookings = []
    
    context = {
        'bookings': bookings,
    }
    
    return render(request, 'client/my_bookings.html', context)

def client_booking_detail_view(request, booking_id):
    """Vista detallada de una reserva del cliente"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para ver esta reserva.')
        return redirect('client_login')
    
    if Booking:
        try:
            booking = Booking.objects.get(
                id=booking_id,
                client__user=request.user
            )
        except Booking.DoesNotExist:
            messages.error(request, 'Reserva no encontrada.')
            return redirect('client_my_bookings')
    else:
        booking = None
        messages.error(request, 'Sistema de reservas no disponible.')
        return redirect('client_my_bookings')
    
    context = {
        'booking': booking,
    }
    
    return render(request, 'client/booking_detail.html', context)

def client_cancel_booking_view(request, booking_id):
    """Vista para cancelar una reserva"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para cancelar una reserva.')
        return redirect('client_login')
    
    if request.method == 'POST':
        if Booking:
            try:
                booking = Booking.objects.get(
                    id=booking_id,
                    client__user=request.user,
                    status__in=['pending', 'confirmed']
                )
                booking.cancel_booking()
                messages.success(request, 'Reserva cancelada exitosamente.')
            except Booking.DoesNotExist:
                messages.error(request, 'Reserva no encontrada o no se puede cancelar.')
        else:
            messages.error(request, 'Sistema de reservas no disponible.')
    
    return redirect('client_my_bookings')

def client_profile_view(request):
    """Vista del perfil del cliente"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para ver tu perfil.')
        return redirect('client_login')
    
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        # Actualizar información del cliente si existe
        if hasattr(request.user, 'client') and Client:
            client = request.user.client
            client.phone = request.POST.get('phone', client.phone)
            client.address = request.POST.get('address', client.address)
            client.nationality = request.POST.get('nationality', client.nationality)
            client.save()
        
        messages.success(request, 'Perfil actualizado exitosamente.')
        return redirect('client_profile')
    
    context = {
        'client': getattr(request.user, 'client', None) if Client else None,
    }
    
    return render(request, 'client/profile.html', context)

def client_login_view(request):
    """Vista de login para clientes"""
    if request.user.is_authenticated:
        return redirect('client_index')
    
    # Obtener el username del parámetro GET si viene del registro
    username_from_register = request.GET.get('username', '')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if not remember:
                request.session.set_expiry(0)
            messages.success(request, f'¡Bienvenido, {user.get_full_name() or user.username}!')
            return redirect('client_index')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'client/login.html', {'username_from_register': username_from_register})

def client_register_view(request):
    """Vista de registro para clientes con validaciones mejoradas"""
    if request.user.is_authenticated:
        return redirect('client_index')
    
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # El cliente se creará automáticamente mediante las señales
            # Actualizar campos adicionales si se proporcionaron
            try:
                # Esperar a que las señales creen el cliente
                from django.db import transaction
                transaction.on_commit(lambda: update_client_additional_fields(user, form.cleaned_data))
            except Exception as e:
                # Si hay error, continuar sin los campos adicionales
                pass
            
            # En lugar de hacer login automático, redirigir al login con el username
            messages.success(request, '¡Cuenta creada exitosamente! Ahora puedes iniciar sesión con tus credenciales.')
            # Redirigir al login con el username como parámetro
            return redirect(f'/portal/login/?username={user.username}')
        else:
            # Los errores se mostrarán automáticamente en el template
            pass
    else:
        form = ClientRegistrationForm()
    
    return render(request, 'client/register.html', {'form': form})

def client_logout_view(request):
    """Vista para cerrar sesión de clientes"""
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('client_index')

def update_client_additional_fields(user, form_data):
    """Función auxiliar para actualizar campos adicionales del cliente"""
    try:
        if hasattr(user, 'client'):
            client = user.client
            if form_data.get('phone'):
                client.phone = form_data.get('phone')
            if form_data.get('address'):
                client.address = form_data.get('address')
            if form_data.get('nationality'):
                client.nationality = form_data.get('nationality')
            client.save()
    except Exception:
        pass  # Ignorar errores silenciosamente


def client_simulate_payment_view(request, booking_id):
    """Simula el pago de una reserva desde el portal del cliente."""
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para realizar pagos.')
        return redirect('client_login')

    if request.method != 'POST':
        messages.error(request, 'Método no permitido.')
        return redirect('client_booking_detail', booking_id=booking_id)

    try:
        from django.db import transaction
        with transaction.atomic():
            booking = Booking.objects.select_for_update().get(
                id=booking_id,
                client__user=request.user
            )

            if booking.status not in ['pending', 'confirmed']:
                messages.error(request, 'La reserva no está en estado válido para pago.')
                return redirect('client_booking_detail', booking_id=booking_id)

            # Simulación de pago con soporte de monto parcial
            result = request.POST.get('result', 'success')
            from decimal import Decimal, InvalidOperation

            if result == 'partial':
                amount_str = request.POST.get('amount')
                if not amount_str:
                    messages.error(request, 'Debes ingresar un monto para el pago parcial.')
                    return redirect('client_booking_detail', booking_id=booking_id)
                try:
                    amount = Decimal(amount_str)
                except (InvalidOperation, TypeError):
                    messages.error(request, 'Monto inválido para pago parcial.')
                    return redirect('client_booking_detail', booking_id=booking_id)
                if amount <= Decimal('0'):
                    messages.error(request, 'El monto debe ser mayor a 0.')
                    return redirect('client_booking_detail', booking_id=booking_id)

                # Acumular pagos parciales
                current_paid = booking.paid_amount or Decimal('0')
                new_paid = current_paid + amount

                # Determinar estado según total
                total = booking.total_price or Decimal('0')
                if new_paid >= total:
                    booking.payment_status = 'paid'
                    booking.paid_amount = total
                else:
                    booking.payment_status = 'partial'
                    booking.paid_amount = new_paid

            else:
                # Pago exitoso total
                booking.payment_status = 'paid'
                booking.paid_amount = booking.total_price

            booking.save()

        # Enviar email de confirmación/recibo de pago
        try:
            from .services import EmailService
            EmailService.send_payment_confirmation(booking.id)
        except Exception:
            import logging
            logging.getLogger(__name__).warning(f"Fallo el envío de email de pago para reserva {booking.id}")

        messages.success(request, 'Pago simulado procesado correctamente.')
        return redirect('client_booking_detail', booking_id=booking_id)

    except Booking.DoesNotExist:
        messages.error(request, 'Reserva no encontrada.')
        return redirect('client_my_bookings')
    except Exception:
        messages.error(request, 'Ocurrió un error al procesar el pago simulado.')
        return redirect('client_booking_detail', booking_id=booking_id)

# --- PDF de Reserva (Cliente) ---
@login_required
def client_booking_pdf_view(request, booking_id):
    """Genera y descarga un PDF simple con los datos de la reserva del cliente."""
    # Restringir a que el usuario sea dueño de la reserva (si no es staff)
    try:
        if request.user.is_staff:
            booking = Booking.objects.get(id=booking_id)
        else:
            booking = Booking.objects.get(id=booking_id, client__user=request.user)
    except Booking.DoesNotExist:
        messages.error(request, 'Reserva no encontrada.')
        return redirect('client_my_bookings')

    # Generar PDF con ReportLab
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reserva_{booking.id}.pdf"'

        c = canvas.Canvas(response, pagesize=A4)
        width, height = A4

        # Encabezado
        c.setFont("Helvetica-Bold", 16)
        c.drawString(20*mm, height - 25*mm, "O11CE Hotel - Detalle de Reserva")
        c.setFont("Helvetica", 10)
        c.drawString(20*mm, height - 32*mm, f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        # Datos de reserva
        y = height - 50*mm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(20*mm, y, f"Reserva #{booking.id}")
        y -= 8*mm
        c.setFont("Helvetica", 11)
        c.drawString(20*mm, y, f"Habitación: {booking.room.get_type_display} (N° {booking.room.number})")
        y -= 7*mm
        c.drawString(20*mm, y, f"Check-in: {booking.check_in_date.strftime('%d/%m/%Y')}  -  Check-out: {booking.check_out_date.strftime('%d/%m/%Y')}")
        y -= 7*mm
        c.drawString(20*mm, y, f"Duración: {booking.duration} noche(s)")
        y -= 7*mm
        c.drawString(20*mm, y, f"Huéspedes: {booking.guests_count}")
        y -= 7*mm
        c.drawString(20*mm, y, f"Estado: {booking.status}")
        y -= 7*mm
        c.drawString(20*mm, y, f"Pago: {booking.payment_status}")
        y -= 7*mm
        c.drawString(20*mm, y, f"Total: ${booking.total_price}")
        
        # Solicitudes especiales
        if booking.special_requests:
            y -= 12*mm
            c.setFont("Helvetica-Bold", 12)
            c.drawString(20*mm, y, "Solicitudes Especiales:")
            y -= 7*mm
            c.setFont("Helvetica", 10)
            # Partir texto si es largo
            import textwrap
            for line in textwrap.wrap(booking.special_requests, width=80):
                c.drawString(20*mm, y, line)
                y -= 6*mm

        # Pie de página
        c.setFont("Helvetica", 9)
        c.drawString(20*mm, 15*mm, "Gracias por elegir O11CE Hotel. Tel: +1234567890 | soporte@o11ce.com")

        c.showPage()
        c.save()
        return response
    except Exception:
        messages.error(request, 'No se pudo generar el PDF. Contacta soporte.')
        return redirect('client_booking_detail', booking_id=booking_id)
