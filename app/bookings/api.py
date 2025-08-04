from ninja import Router, Schema
from typing import Optional
from datetime import date
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Booking
from app.clients.models import Client
from app.rooms.models import Room
from app.core.services import EmailService

router = Router()

# Schemas para la API
class CreateBookingRequest(Schema):
    nombre: str
    email: str
    telefono: Optional[str] = None
    dni: str
    habitacion_id: int
    fecha_inicio: date
    fecha_fin: date
    solicitudes_especiales: Optional[str] = None

class BookingResponse(Schema):
    success: bool
    message: str
    booking_id: Optional[int] = None
    client_id: Optional[int] = None
    total_price: Optional[float] = None

@router.post("/reservas/crear-con-cliente/", response=BookingResponse)
def create_booking_with_client(request, payload: CreateBookingRequest):
    """
    Crea el cliente si no existe y luego la reserva, validando disponibilidad.
    
    Args:
        payload: Datos del cliente y la reserva
    
    Returns:
        Información de la reserva creada
    """
    try:
        with transaction.atomic():
            # Inicializar variables
            created = False
            
            # Validaciones básicas
            if payload.fecha_inicio >= payload.fecha_fin:
                return {
                    "success": False,
                    "message": "La fecha de inicio debe ser anterior a la fecha de fin",
                    "booking_id": None,
                    "client_id": None,
                    "total_price": None
                }
            
            # Verificar que la habitación existe
            try:
                room = Room.objects.get(id=payload.habitacion_id)
            except Room.DoesNotExist:
                return {
                    "success": False,
                    "message": "La habitación especificada no existe",
                    "booking_id": None,
                    "client_id": None,
                    "total_price": None
                }
            
            # Verificar que la habitación esté disponible
            if not room.available_for_booking:
                return {
                    "success": False,
                    "message": "La habitación no está disponible para reservas",
                    "booking_id": None,
                    "client_id": None,
                    "total_price": None
                }
            
            # Verificar que no haya reservas superpuestas
            conflicting_bookings = Booking.objects.filter(
                room=room,
                status__in=['pending', 'confirmed'],
                check_in_date__lt=payload.fecha_fin,
                check_out_date__gt=payload.fecha_inicio
            )
            
            if conflicting_bookings.exists():
                return {
                    "success": False,
                    "message": "La habitación no está disponible para las fechas solicitadas",
                    "booking_id": None,
                    "client_id": None,
                    "total_price": None
                }
            
            # Buscar cliente por email o DNI
            try:
                # Primero intentar buscar por email
                client = Client.objects.get(email=payload.email)
                client_found_by_email = True
            except Client.DoesNotExist:
                try:
                    # Si no existe por email, buscar por DNI
                    client = Client.objects.get(dni=payload.dni)
                    client_found_by_email = False
                except Client.DoesNotExist:
                    # Si no existe por ninguno, crear nuevo cliente
                    client = Client.objects.create(
                        first_name=payload.nombre.split()[0] if payload.nombre else '',
                        last_name=' '.join(payload.nombre.split()[1:]) if len(payload.nombre.split()) > 1 else '',
                        email=payload.email,
                        phone=payload.telefono,
                        dni=payload.dni,
                    )
                    client_found_by_email = False
                    created = True
            
            # Si el cliente ya existía, actualizar datos si es necesario
            if not created:
                updated = False
                
                # Actualizar email si es diferente y no está en uso
                if payload.email != client.email:
                    try:
                        # Verificar que el nuevo email no esté en uso
                        Client.objects.get(email=payload.email)
                        # Si llegamos aquí, el email ya está en uso por otro cliente
                        return {
                            "success": False,
                            "message": f"El email {payload.email} ya está registrado por otro cliente",
                            "booking_id": None,
                            "client_id": None,
                            "total_price": None
                        }
                    except Client.DoesNotExist:
                        client.email = payload.email
                        updated = True
                
                # Actualizar DNI si es diferente y no está en uso
                if payload.dni != client.dni:
                    try:
                        # Verificar que el nuevo DNI no esté en uso
                        Client.objects.get(dni=payload.dni)
                        # Si llegamos aquí, el DNI ya está en uso por otro cliente
                        return {
                            "success": False,
                            "message": f"El DNI {payload.dni} ya está registrado por otro cliente",
                            "booking_id": None,
                            "client_id": None,
                            "total_price": None
                        }
                    except Client.DoesNotExist:
                        client.dni = payload.dni
                        updated = True
                
                # Actualizar otros campos si están vacíos
                if not client.phone and payload.telefono:
                    client.phone = payload.telefono
                    updated = True
                
                if not client.first_name and payload.nombre:
                    client.first_name = payload.nombre.split()[0] if payload.nombre else ''
                    client.last_name = ' '.join(payload.nombre.split()[1:]) if len(payload.nombre.split()) > 1 else ''
                    updated = True
                
                if updated:
                    client.save()
            
            # Calcular precio total
            duration = (payload.fecha_fin - payload.fecha_inicio).days
            total_price = room.price * duration
            
            # Crear la reserva
            booking = Booking.objects.create(
                client=client,
                room=room,
                check_in_date=payload.fecha_inicio,
                check_out_date=payload.fecha_fin,
                status='confirmed',  # Estado confirmada como se solicita
                payment_status='pending',
                guests_count=room.capacity,  # Usar capacidad de la habitación
                special_requests=payload.solicitudes_especiales,
                total_price=total_price
            )
            
            # Cambiar estado de la habitación a reservada
            room.change_status('reserved')
            
            # Intentar enviar email de confirmación
            email_result = EmailService.send_booking_confirmation(booking.id)
            
            return {
                "success": True,
                "message": f"Reserva creada exitosamente. Cliente {'creado' if created else 'encontrado'}.",
                "booking_id": booking.id,
                "client_id": client.id,
                "total_price": float(total_price),
                "email_sent": email_result["success"],
                "email_message": email_result["message"]
            }
            
    except ValidationError as e:
        return {
            "success": False,
            "message": f"Error de validación: {str(e)}",
            "booking_id": None,
            "client_id": None,
            "total_price": None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error al crear la reserva: {str(e)}",
            "booking_id": None,
            "client_id": None,
            "total_price": None
        }

@router.post("/reservas/{booking_id}/reenviar-email/", response=dict)
def resend_booking_confirmation_email(request, booking_id: int):
    """
    Reenvía el email de confirmación de una reserva existente
    
    Args:
        booking_id: ID de la reserva
        
    Returns:
        Resultado del envío del email
    """
    try:
        booking = get_object_or_404(Booking, id=booking_id)
        
        # Verificar que la reserva esté confirmada
        if booking.status != 'confirmed':
            return {
                "success": False,
                "message": "Solo se pueden reenviar emails para reservas confirmadas"
            }
        
        # Enviar email de confirmación
        result = EmailService.send_booking_confirmation(booking_id)
        
        return {
            "success": result["success"],
            "message": result["message"],
            "booking_id": booking_id,
            "email_log_id": result.get("email_log_id")
        }
        
    except Booking.DoesNotExist:
        return {
            "success": False,
            "message": "Reserva no encontrada"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error al reenviar email: {str(e)}"
        } 