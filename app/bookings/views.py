from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import Booking
from app.rooms.models import Room
from app.clients.models import Client
from app.core.services import EmailService

def booking_step1(request):
    """Paso 1: Selección de fechas y número de personas"""
    if request.method == 'POST':
        # Guardar datos en sesión
        request.session['booking_data'] = {
            'guests_count': request.POST.get('guests_count'),
            'check_in_date': request.POST.get('check_in_date'),
            'check_out_date': request.POST.get('check_out_date'),
        }
        return redirect('booking_step2')
    
    # Establecer fechas por defecto
    today = timezone.now().date()
    default_check_in = today + timedelta(days=1)
    default_check_out = today + timedelta(days=2)
    
    context = {
        'default_check_in': default_check_in,
        'default_check_out': default_check_out,
    }
    return render(request, 'client/booking/step1.html', context)

def booking_step2(request):
    """Paso 2: Selección de habitación disponible"""
    # Verificar que tenemos los datos del paso 1
    booking_data = request.session.get('booking_data')
    if not booking_data:
        messages.error(request, 'Por favor, complete el paso 1 primero.')
        return redirect('booking_step1')
    
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        if room_id:
            booking_data['room_id'] = room_id
            request.session['booking_data'] = booking_data
            return redirect('booking_step3')
    
    # Obtener habitaciones disponibles
    check_in = datetime.strptime(booking_data['check_in_date'], '%Y-%m-%d').date()
    check_out = datetime.strptime(booking_data['check_out_date'], '%Y-%m-%d').date()
    guests_count = int(booking_data['guests_count'])
    
    # Filtrar habitaciones disponibles
    available_rooms = Room.objects.filter(
        active=True,
        capacity__gte=guests_count,
        status='available'
    ).exclude(
        booking__check_in_date__lt=check_out,
        booking__check_out_date__gt=check_in,
        booking__status__in=['pending', 'confirmed']
    ).distinct()
    
    # Calcular precio total para cada habitación
    for room in available_rooms:
        duration = (check_out - check_in).days
        room.total_price = room.price * duration
    
    context = {
        'rooms': available_rooms,
        'booking_data': booking_data,
        'check_in': check_in,
        'check_out': check_out,
        'guests_count': guests_count,
        'duration': (check_out - check_in).days,
    }
    return render(request, 'client/booking/step2.html', context)

def booking_step3(request):
    """Paso 3: Datos personales del cliente"""
    # Verificar que tenemos los datos de los pasos anteriores
    booking_data = request.session.get('booking_data')
    if not booking_data or 'room_id' not in booking_data:
        messages.error(request, 'Por favor, complete los pasos anteriores primero.')
        return redirect('booking_step1')
    
    if request.method == 'POST':
        # Guardar datos personales
        booking_data.update({
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'dni': request.POST.get('dni'),
            'special_requests': request.POST.get('special_requests', ''),
        })
        request.session['booking_data'] = booking_data
        return redirect('booking_step4')
    
    # Pre-llenar datos si el usuario está autenticado
    user_data = {}
    if request.user.is_authenticated:
        user_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        # Intentar obtener datos del cliente
        try:
            client = Client.objects.get(user=request.user)
            user_data.update({
                'phone': client.phone,
                'dni': client.dni,
            })
        except Client.DoesNotExist:
            pass
    
    context = {
        'booking_data': booking_data,
        'user_data': user_data,
    }
    return render(request, 'client/booking/step3.html', context)

def booking_step4(request):
    """Paso 4: Confirmación y resumen"""
    # Verificar que tenemos todos los datos necesarios
    booking_data = request.session.get('booking_data')
    if not booking_data or not all(key in booking_data for key in ['room_id', 'first_name', 'email']):
        messages.error(request, 'Por favor, complete todos los pasos anteriores.')
        return redirect('booking_step1')
    
    # Obtener la habitación
    try:
        room = Room.objects.get(id=booking_data['room_id'])
    except Room.DoesNotExist:
        messages.error(request, 'La habitación seleccionada no existe.')
        return redirect('booking_step2')
    
    # Calcular precio total
    check_in = datetime.strptime(booking_data['check_in_date'], '%Y-%m-%d').date()
    check_out = datetime.strptime(booking_data['check_out_date'], '%Y-%m-%d').date()
    duration = (check_out - check_in).days
    total_price = room.price * duration
    
    context = {
        'booking_data': booking_data,
        'room': room,
        'check_in': check_in,
        'check_out': check_out,
        'duration': duration,
        'total_price': total_price,
    }
    return render(request, 'client/booking/step4.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def create_booking_final(request):
    """Crear la reserva final"""
    try:
        booking_data = request.session.get('booking_data')
        if not booking_data:
            return JsonResponse({
                'success': False,
                'message': 'No se encontraron datos de reserva'
            })
        
        # Obtener la habitación
        try:
            room = Room.objects.get(id=booking_data['room_id'])
        except Room.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'La habitación seleccionada no existe'
            })
        
        # Verificar disponibilidad una vez más
        check_in = datetime.strptime(booking_data['check_in_date'], '%Y-%m-%d').date()
        check_out = datetime.strptime(booking_data['check_out_date'], '%Y-%m-%d').date()
        
        conflicting_bookings = Booking.objects.filter(
            room=room,
            status__in=['pending', 'confirmed'],
            check_in_date__lt=check_out,
            check_out_date__gt=check_in
        )
        
        if conflicting_bookings.exists():
            return JsonResponse({
                'success': False,
                'message': 'La habitación ya no está disponible para las fechas seleccionadas'
            })
        
        # Crear o obtener el cliente
        client, created = Client.objects.get_or_create(
            email=booking_data['email'],
            defaults={
                'first_name': booking_data['first_name'],
                'last_name': booking_data['last_name'],
                'phone': booking_data.get('phone', ''),
                'dni': booking_data.get('dni', ''),
                'user': request.user if request.user.is_authenticated else None,
            }
        )
        
        # Si el cliente ya existía, actualizar datos si es necesario
        if not created:
            if not client.first_name:
                client.first_name = booking_data['first_name']
            if not client.last_name:
                client.last_name = booking_data['last_name']
            if not client.phone and booking_data.get('phone'):
                client.phone = booking_data['phone']
            if not client.dni and booking_data.get('dni'):
                client.dni = booking_data['dni']
            if not client.user and request.user.is_authenticated:
                client.user = request.user
            client.save()
        
        # Calcular precio total
        duration = (check_out - check_in).days
        total_price = room.price * duration
        
        # Crear la reserva
        booking = Booking.objects.create(
            client=client,
            room=room,
            check_in_date=check_in,
            check_out_date=check_out,
            status='confirmed',
            payment_status='pending',
            guests_count=int(booking_data['guests_count']),
            special_requests=booking_data.get('special_requests', ''),
            total_price=total_price
        )
        
        # Cambiar estado de la habitación
        room.change_status('reserved')
        
        # Enviar email de confirmación
        email_result = EmailService.send_booking_confirmation(booking.id)
        
        # Limpiar datos de sesión
        if 'booking_data' in request.session:
            del request.session['booking_data']
        
        return JsonResponse({
            'success': True,
            'message': 'Reserva creada exitosamente',
            'booking_id': booking.id,
            'email_sent': email_result.get('success', False),
            'redirect_url': f'/portal/my-bookings/{booking.id}/'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al crear la reserva: {str(e)}'
        })

@login_required
def booking_detail(request, booking_id):
    """Detalle de la reserva"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Verificar que el usuario puede ver esta reserva
    if not request.user.is_staff and booking.client.user != request.user:
        messages.error(request, 'No tienes permisos para ver esta reserva.')
        return redirect('client_my_bookings')
    
    context = {
        'booking': booking,
    }
    return render(request, 'client/booking/detail.html', context)

@login_required
def my_bookings(request):
    """Lista de reservas del usuario"""
    if request.user.is_staff:
        bookings = Booking.objects.all().order_by('-created_at')
    else:
        try:
            client = Client.objects.get(user=request.user)
            bookings = Booking.objects.filter(client=client).order_by('-created_at')
        except Client.DoesNotExist:
            bookings = Booking.objects.none()
    
    context = {
        'bookings': bookings,
    }
    return render(request, 'client/booking/my_bookings.html', context)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def cancel_booking(request, booking_id):
    """Cancelar una reserva"""
    try:
        booking = get_object_or_404(Booking, id=booking_id)
        
        # Verificar que el usuario puede cancelar esta reserva
        if not request.user.is_staff and booking.client.user != request.user:
            return JsonResponse({
                'success': False,
                'message': 'No tienes permisos para cancelar esta reserva.'
            })
        
        # Verificar que la reserva se puede cancelar
        if booking.status == 'cancelled':
            return JsonResponse({
                'success': False,
                'message': 'Esta reserva ya ha sido cancelada.'
            })
        
        if booking.status == 'completed':
            return JsonResponse({
                'success': False,
                'message': 'No se puede cancelar una reserva completada.'
            })
        
        # Cancelar la reserva
        booking.cancel_booking()
        
        # Enviar email de cancelación
        try:
            EmailService.send_booking_cancellation(booking.id)
        except Exception as e:
            # Log del error pero no fallar la cancelación
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al enviar email de cancelación para reserva {booking.id}: {str(e)}")
        
        return JsonResponse({
            'success': True,
            'message': 'Reserva cancelada exitosamente',
            'redirect_url': '/client/my-bookings/'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al cancelar la reserva: {str(e)}'
        })
