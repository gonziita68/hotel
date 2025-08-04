from django.db import models
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
import re

class Client(models.Model):
    """
    Modelo para representar los clientes/huéspedes del hotel
    """
    # Campos básicos
    first_name = models.CharField(max_length=100, help_text="Nombre del cliente")
    last_name = models.CharField(max_length=100, help_text="Apellido del cliente")
    email = models.EmailField(unique=True, help_text="Email del cliente")
    phone = models.CharField(max_length=20, blank=True, null=True, help_text="Teléfono del cliente")
    dni = models.CharField(max_length=20, unique=True, help_text="DNI o documento de identidad")
    
    # Campos adicionales
    address = models.TextField(blank=True, null=True, help_text="Dirección del cliente")
    birth_date = models.DateField(blank=True, null=True, help_text="Fecha de nacimiento")
    nationality = models.CharField(max_length=50, blank=True, null=True, help_text="Nacionalidad")
    
    # Campos de control
    active = models.BooleanField(default=True, help_text="Si el cliente está activo en el sistema")
    vip = models.BooleanField(default=False, help_text="Si es cliente VIP")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        """Retorna el nombre completo del cliente"""
        return f"{self.first_name} {self.last_name}"
    
    def clean(self):
        """Validación personalizada del modelo"""
        super().clean()
        
        # Validar formato del DNI
        if self.dni:
            # Patrón básico para DNI argentino (puedes ajustar según tu país)
            dni_pattern = re.compile(r'^\d{7,8}$')
            if not dni_pattern.match(self.dni):
                raise ValidationError({'dni': 'El DNI debe tener 7 u 8 dígitos numéricos'})
        
        # Validar formato del teléfono
        if self.phone:
            phone_pattern = re.compile(r'^\+?[\d\s\-\(\)]+$')
            if not phone_pattern.match(self.phone):
                raise ValidationError({'phone': 'El formato del teléfono no es válido'})
    
    def get_booking_history(self):
        """Retorna el historial completo de reservas del cliente"""
        return self.booking_set.all().order_by('-created_at')
    
    def get_active_bookings(self):
        """Retorna las reservas activas del cliente"""
        return self.booking_set.filter(status__in=['confirmed', 'pending']).order_by('check_in_date')
