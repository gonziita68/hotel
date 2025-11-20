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
from django.db.models import Q
from django.http import HttpResponse
import csv

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
        client.hotel = getattr(room, 'hotel', None)
        client.save()
        
        # Calcular precio total
        duration = (check_out - check_in).days
        total_price = room.price * duration
        
        # Crear la reserva
        booking = Booking.objects.create(
            hotel=room.hotel,
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
    hotel_param = request.GET.get('hotel')
    if hotel_param:
        try:
            hotel_ref = int(hotel_param)
            booking = get_object_or_404(Booking, id=booking_id, hotel_id=hotel_ref)
        except Exception:
            booking = get_object_or_404(Booking, id=booking_id)
    else:
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

@login_required
@require_http_methods(["GET"])
def bookings_api(request):
    """API: Listar reservas con filtros"""
    qs = Booking.objects.select_related('client', 'room').all().order_by('-created_at')
    hotel_id = request.GET.get('hotel')
    if hotel_id:
        try:
            qs = qs.filter(hotel_id=int(hotel_id))
        except Exception:
            pass

    status = request.GET.get('status')
    payment = request.GET.get('payment')
    check_in = request.GET.get('check_in')
    search = request.GET.get('search')

    if status:
        qs = qs.filter(status=status)
    if payment:
        qs = qs.filter(payment_status=payment)
    if check_in:
        qs = qs.filter(check_in_date=check_in)
    if search:
        qs = qs.filter(Q(client__full_name__icontains=search) | Q(room__number__icontains=search))

    data = []
    for b in qs:
        data.append({
            'id': b.id,
            'client': {
                'id': b.client.id,
                'full_name': getattr(b.client, 'full_name', str(b.client)),
                'email': getattr(b.client, 'email', ''),
            },
            'room': {
                'id': b.room.id if b.room else None,
                'number': b.room.number if b.room else '',
                'type': b.room.type if b.room else '',
                'price': float(b.room.price) if b.room and b.room.price is not None else 0,
            },
            'check_in_date': b.check_in_date.isoformat() if b.check_in_date else None,
            'check_out_date': b.check_out_date.isoformat() if b.check_out_date else None,
            'duration': b.duration,
            'total_price': float(b.total_price) if b.total_price is not None else 0,
            'status': b.status,
            'payment_status': b.payment_status,
            'guests_count': b.guests_count,
            'special_requests': b.special_requests or '',
            'created_at': b.created_at.isoformat() if b.created_at else None,
        })
    return JsonResponse(data, safe=False)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_booking_api(request):
    """API: Crear una reserva desde el dashboard"""
    try:
        payload = json.loads(request.body)

        required = ['client_id', 'room_id', 'check_in_date', 'check_out_date', 'guests_count']
        for field in required:
            if not payload.get(field):
                return JsonResponse({'error': f'Campo requerido: {field}'}, status=400)

        client = get_object_or_404(Client, id=payload['client_id'])
        room = get_object_or_404(Room, id=payload['room_id'])
        check_in = datetime.strptime(payload['check_in_date'], '%Y-%m-%d').date()
        check_out = datetime.strptime(payload['check_out_date'], '%Y-%m-%d').date()

        if check_in >= check_out:
            return JsonResponse({'error': 'La fecha de salida debe ser posterior a la de llegada'}, status=400)

        # Verificar conflictos de fechas para la habitación
        conflicts = Booking.objects.filter(
            room=room,
            status__in=['pending', 'confirmed'],
            check_in_date__lt=check_out,
            check_out_date__gt=check_in
        )
        if conflicts.exists():
            return JsonResponse({'error': 'La habitación no está disponible para las fechas seleccionadas'}, status=400)

        status_val = payload.get('status', 'confirmed')
        payment_status_val = payload.get('payment_status', 'pending')
        guests_count = int(payload.get('guests_count', 1))
        special_requests = payload.get('special_requests', '')

        duration = (check_out - check_in).days
        total_price = room.price * duration

        # Asegurar asociación de hotel
        if getattr(client, 'hotel_id', None) != getattr(room, 'hotel_id', None):
            client.hotel = getattr(room, 'hotel', None)
            try:
                client.save(update_fields=['hotel'])
            except Exception:
                client.save()
        booking = Booking.objects.create(
            hotel=getattr(room, 'hotel', None),
            client=client,
            room=room,
            check_in_date=check_in,
            check_out_date=check_out,
            status=status_val,
            payment_status=payment_status_val,
            guests_count=guests_count,
            special_requests=special_requests,
            total_price=total_price
        )

        # Cambiar estado de la habitación si corresponde
        if booking.status in ['pending', 'confirmed']:
            room.change_status('reserved')

        return JsonResponse({
            'id': booking.id,
            'message': 'Reserva creada exitosamente'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Endpoint unificado /api/bookings/ (GET y POST)
@login_required
@csrf_exempt
@require_http_methods(["GET", "POST"])
def bookings_api_collection(request):
    if request.method == "GET":
        return bookings_api(request)
    else:
        return create_booking_api(request)

@login_required
@csrf_exempt
@require_http_methods(["PUT"])
def update_booking_api(request, booking_id):
    """API: Actualizar reserva (fechas, habitación, estado, pago, etc.)"""
    try:
        booking = get_object_or_404(Booking, id=booking_id)
        data = json.loads(request.body)

        # Posibles cambios de fechas/habitación: validar disponibilidad
        new_room_id = data.get('room_id', booking.room.id if booking.room else None)
        new_check_in = data.get('check_in_date', booking.check_in_date.isoformat() if booking.check_in_date else None)
        new_check_out = data.get('check_out_date', booking.check_out_date.isoformat() if booking.check_out_date else None)

        # Si cambian fechas o habitación, verificar conflictos
        if new_room_id and new_check_in and new_check_out:
            room = get_object_or_404(Room, id=new_room_id)
            ci = datetime.strptime(new_check_in, '%Y-%m-%d').date()
            co = datetime.strptime(new_check_out, '%Y-%m-%d').date()
            if ci >= co:
                return JsonResponse({'error': 'La fecha de salida debe ser posterior a la de llegada'}, status=400)

            conflicts = Booking.objects.filter(
                room=room,
                status__in=['pending', 'confirmed'],
                check_in_date__lt=co,
                check_out_date__gt=ci
            ).exclude(id=booking.id)
            if conflicts.exists():
                return JsonResponse({'error': 'La habitación no está disponible para las nuevas fechas'}, status=400)

            booking.room = room
            booking.check_in_date = ci
            booking.check_out_date = co
            # Recalcular total
            booking.total_price = room.price * ((co - ci).days)

        # Otros campos
        if 'guests_count' in data:
            booking.guests_count = int(data['guests_count'])
        if 'payment_status' in data:
            booking.payment_status = data['payment_status']
        if 'special_requests' in data:
            booking.special_requests = data['special_requests']

        # Cambios de estado con reglas
        if 'status' in data:
            new_status = data['status']
            if new_status == 'cancelled':
                booking.cancel_booking(reason=data.get('cancellation_reason', ''))
            elif new_status == 'completed':
                booking.complete_booking()
            elif new_status == 'confirmed':
                booking.confirm_booking()
            else:
                booking.status = new_status
                booking.save()
        else:
            booking.save()

        return JsonResponse({'id': booking.id, 'message': 'Reserva actualizada exitosamente'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["DELETE"])
def delete_booking_api(request, booking_id):
    """API: Eliminar reserva (restricciones básicas)"""
    try:
        booking = get_object_or_404(Booking, id=booking_id)
        if booking.status in ['confirmed', 'completed']:
            return JsonResponse({'error': 'No se puede eliminar una reserva confirmada o finalizada'}, status=400)
        booking.delete()
        return JsonResponse({'message': 'Reserva eliminada exitosamente'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Endpoint unificado /api/bookings/<id>/ (PUT, DELETE)
@login_required
@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def booking_api_detail(request, booking_id):
    if request.method == "PUT":
        return update_booking_api(request, booking_id)
    else:
        return delete_booking_api(request, booking_id)

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

@login_required
def export_bookings_csv(request):
    """Exporta reservas a CSV con filtros opcionales"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="reservas.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Cliente', 'Email', 'Habitacion', 'Check-in', 'Check-out',
        'Noches', 'Total', 'Estado', 'Pago', 'Creado'
    ])

    qs = Booking.objects.select_related('client', 'room').all().order_by('-created_at')

    status = request.GET.get('status')
    payment = request.GET.get('payment')
    check_in = request.GET.get('check_in')
    search = request.GET.get('search')

    if status:
        qs = qs.filter(status=status)
    if payment:
        qs = qs.filter(payment_status=payment)
    if check_in:
        qs = qs.filter(check_in_date=check_in)
    if search:
        qs = qs.filter(Q(client__full_name__icontains=search) | Q(room__number__icontains=search))

    for b in qs:
        writer.writerow([
            b.id,
            getattr(b.client, 'full_name', str(b.client)),
            getattr(b.client, 'email', ''),
            b.room.number if b.room else '',
            b.check_in_date.isoformat() if b.check_in_date else '',
            b.check_out_date.isoformat() if b.check_out_date else '',
            b.duration,
            float(b.total_price) if b.total_price is not None else 0,
            b.get_status_display() if hasattr(b, 'get_status_display') else b.status,
            b.get_payment_status_display() if hasattr(b, 'get_payment_status_display') else b.payment_status,
            b.created_at.isoformat() if b.created_at else ''
        ])

    return response
