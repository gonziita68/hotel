import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.rooms.models import Room

def check_rooms():
    print("=== DIAGNÓSTICO DE HABITACIONES ===")
    
    # Total de habitaciones
    total_rooms = Room.objects.all().count()
    print(f"Total habitaciones en BD: {total_rooms}")
    
    # Habitaciones activas
    active_rooms = Room.objects.filter(active=True).count()
    print(f"Habitaciones activas: {active_rooms}")
    
    # Habitaciones por estado
    print("\nHabitaciones por estado:")
    for status_code, status_name in Room.STATUS_CHOICES:
        count = Room.objects.filter(status=status_code).count()
        print(f"  {status_name} ({status_code}): {count}")
    
    # Habitaciones por tipo
    print("\nHabitaciones por tipo:")
    for type_code, type_name in Room.TYPE_CHOICES:
        count = Room.objects.filter(type=type_code).count()
        print(f"  {type_name} ({type_code}): {count}")
    
    # Primeras 5 habitaciones
    print("\nPrimeras 5 habitaciones:")
    for room in Room.objects.all()[:5]:
        print(f"  Habitación {room.number}: {room.get_type_display()}")
        print(f"    Estado: {room.get_status_display()} ({room.status})")
        print(f"    Activa: {room.active}")
        print(f"    Precio: ${room.price}")
        print(f"    Capacidad: {room.capacity} personas")
        print()

if __name__ == "__main__":
    check_rooms()