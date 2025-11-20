from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from app.clients.models import Client
from app.rooms.models import Room
from app.administration.models import Hotel
from datetime import timedelta

class Booking(models.Model):
    """
    Modelo para representar las reservas del hotel
    """
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('cancelled', 'Cancelada'),
        ('completed', 'Finalizada'),
        ('no_show', 'No Show'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('partial', 'Pago Parcial'),
        ('refunded', 'Reembolsado'),
    ]
    
    # Relaciones
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True, blank=True, help_text="Hotel de la reserva")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, help_text="Cliente que realiza la reserva")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, help_text="Habitación reservada")
    
    # Fechas
    check_in_date = models.DateField(help_text="Fecha de llegada")
    check_out_date = models.DateField(help_text="Fecha de salida")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Estado y pagos
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Monto pagado")
    
    # Información adicional
    guests_count = models.PositiveIntegerField(default=1, help_text="Número de huéspedes")
    special_requests = models.TextField(blank=True, null=True, help_text="Solicitudes especiales")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio total de la reserva")
    
    # Campos de control
    confirmed_at = models.DateTimeField(blank=True, null=True, help_text="Fecha de confirmación")
    cancelled_at = models.DateTimeField(blank=True, null=True, help_text="Fecha de cancelación")
    cancellation_reason = models.TextField(blank=True, null=True, help_text="Motivo de cancelación")
    
    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['check_in_date', 'check_out_date']),
            models.Index(fields=['status']),
            models.Index(fields=['client']),
        ]
    
    def __str__(self):
        return f"Reserva {self.id} - {self.client.full_name} ({self.check_in_date} a {self.check_out_date})"
    
    def clean(self):
        """Validación personalizada del modelo"""
        super().clean()
        
        # Validar que las fechas sean coherentes
        if self.check_in_date and self.check_out_date:
            if self.check_in_date >= self.check_out_date:
                raise ValidationError('La fecha de salida debe ser posterior a la fecha de llegada')
            
            if self.check_in_date < timezone.now().date():
                raise ValidationError('No se pueden hacer reservas para fechas pasadas')
    
    def save(self, *args, **kwargs):
        """Sobrescribir save para calcular precio total, validar disponibilidad y enviar email"""
        skip_validation = kwargs.pop('skip_validation', False)
        is_new_booking = not self.pk  # Verificar si es una nueva reserva
        
        if is_new_booking and not skip_validation:  # Solo para nuevas reservas
            self.validate_availability()
            self.calculate_total_price()
        
        super().save(*args, **kwargs)
        
        # Enviar email de confirmación automáticamente para nuevas reservas confirmadas
        if is_new_booking and self.status == 'confirmed' and not skip_validation:
            try:
                from app.core.services import EmailService
                EmailService.send_booking_confirmation_async(self.id)
            except Exception as e:
                # Log del error pero no fallar la creación de la reserva
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error al enviar email de confirmación para reserva {self.id}: {str(e)}")
    
    @property
    def duration(self):
        """Retorna la duración de la reserva en días"""
        if self.check_in_date and self.check_out_date:
            return (self.check_out_date - self.check_in_date).days
        return 0
    
    @property
    def subtotal(self):
        """Retorna el subtotal de la reserva (precio por noche * duración)"""
        if self.room and self.duration > 0:
            return self.room.price * self.duration
        return 0
    
    @property
    def taxes(self):
        """Retorna los impuestos de la reserva (10% del subtotal)"""
        from decimal import Decimal
        return round(self.subtotal * Decimal('0.1'), 2)
    
    @property
    def is_active(self):
        """Verifica si la reserva está activa"""
        return self.status in ['pending', 'confirmed']
    
    @property
    def is_confirmed(self):
        """Verifica si la reserva está confirmada"""
        return self.status == 'confirmed'
    
    def calculate_total_price(self):
        """Calcula el precio total de la reserva"""
        if self.room and self.duration > 0:
            self.total_price = self.room.price * self.duration
    
    def validate_availability(self):
        """Valida que la habitación esté disponible para las fechas solicitadas"""
        if not self.room.available_for_booking:
            raise ValidationError('La habitación no está disponible para reservas')
        hotel_ref = self.hotel or getattr(self.room, 'hotel', None)
        if hotel_ref and getattr(hotel_ref, 'is_blocked', False):
            raise ValidationError('El hotel está bloqueado y no acepta nuevas reservas')
        # Verificar coherencia de hotel si está seteado
        if self.hotel and self.room and hasattr(self.room, 'hotel') and self.room.hotel and self.room.hotel != self.hotel:
            raise ValidationError('La habitación seleccionada no pertenece al hotel de la reserva')
        
        # Verificar si hay conflictos con otras reservas
        conflicting_bookings = Booking.objects.filter(
            room=self.room,
            status__in=['pending', 'confirmed'],
            check_in_date__lt=self.check_out_date,
            check_out_date__gt=self.check_in_date
        )
        
        if conflicting_bookings.exists():
            raise ValidationError('La habitación no está disponible para las fechas solicitadas')
    
    def confirm_booking(self):
        """Confirma la reserva"""
        if self.status == 'pending':
            self.status = 'confirmed'
            self.confirmed_at = timezone.now()
            self.room.change_status('reserved')
            self.save()
            return True
        return False
    
    def cancel_booking(self, reason=""):
        """Cancela la reserva"""
        if self.status in ['pending', 'confirmed']:
            self.status = 'cancelled'
            self.cancelled_at = timezone.now()
            self.cancellation_reason = reason
            self.room.change_status('available')
            self.save()
            return True
        return False
    
    def complete_booking(self):
        """Marca la reserva como completada"""
        if self.status == 'confirmed':
            self.status = 'completed'
            self.room.change_status('cleaning')
            self.save()
            return True
        return False
    
    @property
    def amount_due(self):
        """Monto pendiente de pago"""
        from decimal import Decimal
        total = self.total_price or Decimal('0')
        paid = self.paid_amount or Decimal('0')
        due = total - paid
        return due if due > Decimal('0') else Decimal('0')
