#!/usr/bin/env python
"""
Script para poblar la base de datos con datos de ejemplo
Ejecutar con: python manage.py shell < populate_data.py
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.rooms.models import Room
from app.clients.models import Client
from app.bookings.models import Booking

def create_sample_rooms():
    """Crear habitaciones de ejemplo"""
    print("Creando habitaciones de ejemplo...")
    
    rooms_data = [
        # Individuales
        {'number': '101', 'type': 'individual', 'capacity': 1, 'price': Decimal('50.00'), 'floor': 1},
        {'number': '102', 'type': 'individual', 'capacity': 1, 'price': Decimal('50.00'), 'floor': 1},
        {'number': '103', 'type': 'individual', 'capacity': 1, 'price': Decimal('55.00'), 'floor': 1},
        
        # Dobles
        {'number': '201', 'type': 'double', 'capacity': 2, 'price': Decimal('80.00'), 'floor': 2},
        {'number': '202', 'type': 'double', 'capacity': 2, 'price': Decimal('80.00'), 'floor': 2},
        {'number': '203', 'type': 'double', 'capacity': 2, 'price': Decimal('85.00'), 'floor': 2},
        {'number': '204', 'type': 'double', 'capacity': 2, 'price': Decimal('85.00'), 'floor': 2},
        
        # Triples
        {'number': '301', 'type': 'triple', 'capacity': 3, 'price': Decimal('120.00'), 'floor': 3},
        {'number': '302', 'type': 'triple', 'capacity': 3, 'price': Decimal('120.00'), 'floor': 3},
        
        # Suites
        {'number': '401', 'type': 'suite', 'capacity': 2, 'price': Decimal('150.00'), 'floor': 4},
        {'number': '402', 'type': 'suite', 'capacity': 2, 'price': Decimal('160.00'), 'floor': 4},
        
        # Familiares
        {'number': '501', 'type': 'family', 'capacity': 4, 'price': Decimal('180.00'), 'floor': 5},
        {'number': '502', 'type': 'family', 'capacity': 4, 'price': Decimal('180.00'), 'floor': 5},
    ]
    
    for room_data in rooms_data:
        room, created = Room.objects.get_or_create(
            number=room_data['number'],
            defaults=room_data
        )
        if created:
            print(f"✓ Habitación {room.number} creada")
        else:
            print(f"⚠ Habitación {room.number} ya existe")

def create_sample_clients():
    """Crear clientes de ejemplo"""
    print("\nCreando clientes de ejemplo...")
    
    clients_data = [
        {
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'email': 'juan.perez@email.com',
            'phone': '+54 11 1234-5678',
            'dni': '12345678',
            'nationality': 'Argentina'
        },
        {
            'first_name': 'María',
            'last_name': 'González',
            'email': 'maria.gonzalez@email.com',
            'phone': '+54 11 2345-6789',
            'dni': '23456789',
            'nationality': 'Argentina'
        },
        {
            'first_name': 'Carlos',
            'last_name': 'López',
            'email': 'carlos.lopez@email.com',
            'phone': '+54 11 3456-7890',
            'dni': '34567890',
            'nationality': 'Argentina'
        },
        {
            'first_name': 'Ana',
            'last_name': 'Martínez',
            'email': 'ana.martinez@email.com',
            'phone': '+54 11 4567-8901',
            'dni': '45678901',
            'nationality': 'Argentina'
        },
        {
            'first_name': 'Roberto',
            'last_name': 'Fernández',
            'email': 'roberto.fernandez@email.com',
            'phone': '+54 11 5678-9012',
            'dni': '56789012',
            'nationality': 'Argentina',
            'vip': True
        },
    ]
    
    for client_data in clients_data:
        client, created = Client.objects.get_or_create(
            email=client_data['email'],
            defaults=client_data
        )
        if created:
            print(f"✓ Cliente {client.full_name} creado")
        else:
            print(f"⚠ Cliente {client.full_name} ya existe")

def create_sample_bookings():
    """Crear reservas de ejemplo"""
    print("\nCreando reservas de ejemplo...")
    
    # Obtener habitaciones y clientes
    rooms = Room.objects.filter(active=True)
    clients = Client.objects.filter(active=True)
    
    if not rooms.exists():
        print("❌ No hay habitaciones disponibles")
        return
    
    if not clients.exists():
        print("❌ No hay clientes disponibles")
        return
    
    # Crear algunas reservas de ejemplo
    today = date.today()
    
    bookings_data = [
        {
            'client': clients[0],
            'room': rooms[0],
            'check_in_date': today + timedelta(days=5),
            'check_out_date': today + timedelta(days=8),
            'guests_count': 1,
            'status': 'confirmed',
            'payment_status': 'paid'
        },
        {
            'client': clients[1],
            'room': rooms[3],
            'check_in_date': today + timedelta(days=10),
            'check_out_date': today + timedelta(days=15),
            'guests_count': 2,
            'status': 'pending',
            'payment_status': 'pending'
        },
        {
            'client': clients[2],
            'room': rooms[7],
            'check_in_date': today + timedelta(days=20),
            'check_out_date': today + timedelta(days=25),
            'guests_count': 2,
            'status': 'confirmed',
            'payment_status': 'partial'
        },
    ]
    
    for booking_data in bookings_data:
        # Verificar disponibilidad antes de crear
        conflicting_bookings = Booking.objects.filter(
            room=booking_data['room'],
            status__in=['pending', 'confirmed'],
            check_in_date__lt=booking_data['check_out_date'],
            check_out_date__gt=booking_data['check_in_date']
        )
        
        if not conflicting_bookings.exists():
            booking = Booking.objects.create(**booking_data)
            print(f"✓ Reserva {booking.id} creada para {booking.client.full_name}")
        else:
            print(f"⚠ No se pudo crear reserva para {booking_data['client'].full_name} - habitación ocupada")

def main():
    """Función principal"""
    print("=== POBLADO DE DATOS DE EJEMPLO ===\n")
    
    try:
        create_sample_rooms()
        create_sample_clients()
        create_sample_bookings()
        
        print("\n=== RESUMEN ===")
        print(f"Habitaciones: {Room.objects.count()}")
        print(f"Clientes: {Client.objects.count()}")
        print(f"Reservas: {Booking.objects.count()}")
        print("\n✅ Datos de ejemplo creados exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main() 