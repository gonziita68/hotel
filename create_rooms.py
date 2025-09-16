#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from app.rooms.models import Room
from decimal import Decimal

def create_sample_rooms():
    """Crear habitaciones de ejemplo"""
    print("Creando habitaciones de ejemplo...")
    
    rooms_data = [
        # Individuales
        {'number': '101', 'type': 'individual', 'capacity': 1, 'price': Decimal('50.00'), 'floor': 1, 'description': 'Habitacion individual comoda y acogedora'},
        {'number': '102', 'type': 'individual', 'capacity': 1, 'price': Decimal('50.00'), 'floor': 1, 'description': 'Habitacion individual con vista al jardin'},
        {'number': '103', 'type': 'individual', 'capacity': 1, 'price': Decimal('55.00'), 'floor': 1, 'description': 'Habitacion individual premium'},
        
        # Dobles
        {'number': '201', 'type': 'double', 'capacity': 2, 'price': Decimal('80.00'), 'floor': 2, 'description': 'Habitacion doble espaciosa'},
        {'number': '202', 'type': 'double', 'capacity': 2, 'price': Decimal('80.00'), 'floor': 2, 'description': 'Habitacion doble con balcon'},
        {'number': '203', 'type': 'double', 'capacity': 2, 'price': Decimal('85.00'), 'floor': 2, 'description': 'Habitacion doble deluxe'},
        {'number': '204', 'type': 'double', 'capacity': 2, 'price': Decimal('85.00'), 'floor': 2, 'description': 'Habitacion doble con vista panoramica'},
        
        # Triples
        {'number': '301', 'type': 'triple', 'capacity': 3, 'price': Decimal('120.00'), 'floor': 3, 'description': 'Habitacion triple ideal para familias'},
        {'number': '302', 'type': 'triple', 'capacity': 3, 'price': Decimal('120.00'), 'floor': 3, 'description': 'Habitacion triple con espacio adicional'},
        
        # Suites
        {'number': '401', 'type': 'suite', 'capacity': 2, 'price': Decimal('150.00'), 'floor': 4, 'description': 'Suite de lujo con sala de estar'},
        {'number': '402', 'type': 'suite', 'capacity': 2, 'price': Decimal('160.00'), 'floor': 4, 'description': 'Suite ejecutiva premium'},
        
        # Familiares
        {'number': '501', 'type': 'family', 'capacity': 4, 'price': Decimal('180.00'), 'floor': 5, 'description': 'Habitacion familiar amplia'},
        {'number': '502', 'type': 'family', 'capacity': 4, 'price': Decimal('180.00'), 'floor': 5, 'description': 'Habitacion familiar con comodidades extra'},
    ]
    
    created_count = 0
    for room_data in rooms_data:
        room, created = Room.objects.get_or_create(
            number=room_data['number'],
            defaults=room_data
        )
        if created:
            print(f"✓ Habitacion {room.number} creada")
            created_count += 1
        else:
            print(f"- Habitacion {room.number} ya existe")
    
    print(f"\nTotal de habitaciones creadas: {created_count}")
    print(f"Total de habitaciones en la base de datos: {Room.objects.count()}")

if __name__ == '__main__':
    create_sample_rooms()