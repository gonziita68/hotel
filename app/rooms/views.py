from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
import json
from .models import Room, RoomImage
from .forms import RoomForm

@login_required
def rooms_view(request):
    """Vista principal para la gestión de habitaciones"""
    rooms = Room.objects.all().order_by('number')
    
    # Filtros
    status_filter = request.GET.get('status')
    type_filter = request.GET.get('type')
    floor_filter = request.GET.get('floor')
    search = request.GET.get('search')
    
    if status_filter:
        rooms = rooms.filter(status=status_filter)
    if type_filter:
        rooms = rooms.filter(type=type_filter)
    if floor_filter:
        rooms = rooms.filter(floor=floor_filter)
    if search:
        rooms = rooms.filter(
            Q(number__icontains=search) | 
            Q(description__icontains=search)
        )
    
    # Paginación
    paginator = Paginator(rooms, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'rooms': page_obj,
        'room_types': Room.TYPE_CHOICES,
        'room_statuses': Room.STATUS_CHOICES,
        'current_filters': {
            'status': status_filter,
            'type': type_filter,
            'floor': floor_filter,
            'search': search,
        }
    }
    
    return render(request, 'rooms.html', context)

@login_required
def room_detail(request, room_id):
    """Vista de detalle de una habitación"""
    room = get_object_or_404(Room, id=room_id)
    images = RoomImage.objects.filter(room=room)
    
    context = {
        'room': room,
        'images': images,
    }
    
    return render(request, 'room_detail.html', context)

@login_required
def create_room(request):
    """Vista para crear una nueva habitación"""
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'Habitación {room.number} creada exitosamente.')
            return redirect('rooms')
        else:
            messages.error(request, 'Error al crear la habitación. Revisa los datos.')
    else:
        form = RoomForm()
    
    context = {
        'form': form,
        'title': 'Nueva Habitación',
        'action': 'create'
    }
    
    return render(request, 'room_form.html', context)

@login_required
def edit_room(request, room_id):
    """Vista para editar una habitación"""
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'Habitación {room.number} actualizada exitosamente.')
            return redirect('rooms')
        else:
            messages.error(request, 'Error al actualizar la habitación. Revisa los datos.')
    else:
        form = RoomForm(instance=room)
    
    context = {
        'form': form,
        'room': room,
        'title': f'Editar Habitación {room.number}',
        'action': 'edit'
    }
    
    return render(request, 'room_form.html', context)

@login_required
def delete_room(request, room_id):
    """Vista para eliminar una habitación"""
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        room_number = room.number
        room.delete()
        messages.success(request, f'Habitación {room_number} eliminada exitosamente.')
        return redirect('rooms')
    
    context = {
        'room': room,
        'title': f'Eliminar Habitación {room.number}'
    }
    
    return render(request, 'room_confirm_delete.html', context)

# API Views para AJAX
@login_required
@require_http_methods(["GET"])
def rooms_api(request):
    """API para obtener habitaciones en formato JSON"""
    rooms = Room.objects.all().order_by('number')
    
    # Aplicar filtros
    status_filter = request.GET.get('status')
    type_filter = request.GET.get('type')
    floor_filter = request.GET.get('floor')
    search = request.GET.get('search')
    
    if status_filter:
        rooms = rooms.filter(status=status_filter)
    if type_filter:
        rooms = rooms.filter(type=type_filter)
    if floor_filter:
        rooms = rooms.filter(floor=floor_filter)
    if search:
        rooms = rooms.filter(
            Q(number__icontains=search) | 
            Q(description__icontains=search)
        )
    
    rooms_data = []
    for room in rooms:
        rooms_data.append({
            'id': room.id,
            'number': room.number,
            'type': room.type,
            'capacity': room.capacity,
            'floor': room.floor,
            'price': float(room.price),
            'status': room.status,
            'description': room.description or '',
            'active': room.active,
            'created_at': room.created_at.isoformat() if room.created_at else None,
        })
    
    return JsonResponse(rooms_data, safe=False)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_room_api(request):
    """API para crear una habitación"""
    try:
        data = json.loads(request.body)
        
        # Validar que el número de habitación no exista
        if Room.objects.filter(number=data.get('number')).exists():
            return JsonResponse({
                'error': 'Ya existe una habitación con este número'
            }, status=400)
        
        room = Room.objects.create(
            number=data.get('number'),
            type=data.get('type'),
            capacity=data.get('capacity'),
            floor=data.get('floor'),
            price=data.get('price'),
            status=data.get('status', 'available'),
            description=data.get('description', ''),
            active=data.get('active', True)
        )
        
        return JsonResponse({
            'id': room.id,
            'number': room.number,
            'message': 'Habitación creada exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)

# Endpoint unificado para GET y POST en /api/rooms/
@login_required
@csrf_exempt
@require_http_methods(["GET", "POST"])
def rooms_api_collection(request):
    if request.method == "GET":
        return rooms_api(request)
    else:  # POST
        return create_room_api(request)


@login_required
@csrf_exempt
@require_http_methods(["PUT"])
def update_room_api(request, room_id):
    """API para actualizar una habitación"""
    try:
        room = get_object_or_404(Room, id=room_id)
        data = json.loads(request.body)
        
        # Validar que el número de habitación no exista en otra habitación
        if Room.objects.filter(number=data.get('number')).exclude(id=room_id).exists():
            return JsonResponse({
                'error': 'Ya existe otra habitación con este número'
            }, status=400)
        
        room.number = data.get('number', room.number)
        room.type = data.get('type', room.type)
        room.capacity = data.get('capacity', room.capacity)
        room.floor = data.get('floor', room.floor)
        room.price = data.get('price', room.price)
        room.status = data.get('status', room.status)
        room.description = data.get('description', room.description)
        room.active = data.get('active', room.active)
        
        room.save()
        
        return JsonResponse({
            'id': room.id,
            'number': room.number,
            'message': 'Habitación actualizada exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)

# Endpoint unificado para PUT y DELETE en /api/rooms/<id>/
@login_required
@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def room_api_detail(request, room_id):
    if request.method == "PUT":
        return update_room_api(request, room_id)
    else:  # DELETE
        return delete_room_api(request, room_id)

@require_http_methods(["DELETE"])
def delete_room_api(request, room_id):
    """API para eliminar una habitación"""
    try:
        room = get_object_or_404(Room, id=room_id)
        
        # Verificar que no tenga reservas activas
        if hasattr(room, 'bookings') and room.bookings.filter(status__in=['confirmed', 'checked_in']).exists():
            return JsonResponse({
                'error': 'No se puede eliminar una habitación con reservas activas'
            }, status=400)
        
        room_number = room.number
        room.delete()
        
        return JsonResponse({
            'message': f'Habitación {room_number} eliminada exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)

@login_required
def room_status_update(request, room_id):
    """Vista para actualizar rápidamente el estado de una habitación"""
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Room.STATUS_CHOICES):
            room.status = new_status
            room.save()
            messages.success(request, f'Estado de habitación {room.number} actualizado a {room.get_status_display()}.')
        else:
            messages.error(request, 'Estado inválido.')
    
    return redirect('rooms')

@login_required
def rooms_statistics(request):
    """Vista para obtener estadísticas de habitaciones"""
    total_rooms = Room.objects.count()
    available_rooms = Room.objects.filter(status='available').count()
    occupied_rooms = Room.objects.filter(status='occupied').count()
    cleaning_rooms = Room.objects.filter(status='cleaning').count()
    maintenance_rooms = Room.objects.filter(status='maintenance').count()
    reserved_rooms = Room.objects.filter(status='reserved').count()
    
    # Estadísticas por tipo
    room_types_stats = {}
    for room_type, display_name in Room.TYPE_CHOICES:
        room_types_stats[display_name] = Room.objects.filter(type=room_type).count()
    
    # Estadísticas por piso
    floors_stats = {}
    floors = Room.objects.values_list('floor', flat=True).distinct().order_by('floor')
    for floor in floors:
        floors_stats[f'Piso {floor}'] = Room.objects.filter(floor=floor).count()
    
    context = {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'cleaning_rooms': cleaning_rooms,
        'maintenance_rooms': maintenance_rooms,
        'reserved_rooms': reserved_rooms,
        'occupancy_rate': round((occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0, 1),
        'room_types_stats': room_types_stats,
        'floors_stats': floors_stats,
    }
    
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse(context)
    
    return render(request, 'rooms_statistics.html', context)

# Nueva vista: exportación CSV de habitaciones
@login_required
def export_rooms_csv(request):
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="habitaciones.csv"'

    writer = csv.writer(response)
    # Encabezados
    writer.writerow([
        'Numero', 'Tipo', 'Capacidad', 'Piso', 'Precio', 'Estado', 'Activa', 'Descripcion'
    ])

    # Filtros opcionales (coherentes con la vista)
    rooms_qs = Room.objects.all().order_by('number')
    status_filter = request.GET.get('status')
    type_filter = request.GET.get('type')
    floor_filter = request.GET.get('floor')
    search = request.GET.get('search')

    if status_filter:
        rooms_qs = rooms_qs.filter(status=status_filter)
    if type_filter:
        rooms_qs = rooms_qs.filter(type=type_filter)
    if floor_filter:
        rooms_qs = rooms_qs.filter(floor=floor_filter)
    if search:
        rooms_qs = rooms_qs.filter(Q(number__icontains=search) | Q(description__icontains=search))

    for room in rooms_qs:
        writer.writerow([
            room.number,
            room.get_type_display() if hasattr(room, 'get_type_display') else room.type,
            room.capacity,
            room.floor,
            room.price,
            room.get_status_display() if hasattr(room, 'get_status_display') else room.status,
            'Sí' if room.active else 'No',
            (room.description or '').replace('\n', ' ').strip()
        ])

    return response
