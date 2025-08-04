from django.db import models

class Room(models.Model):
    """
    Modelo para representar las habitaciones del hotel
    """
    TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('double', 'Doble'),
        ('triple', 'Triple'),
        ('suite', 'Suite'),
        ('family', 'Familiar'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Libre'),
        ('occupied', 'Ocupada'),
        ('cleaning', 'En Limpieza'),
        ('maintenance', 'En Mantenimiento'),
        ('reserved', 'Reservada'),
    ]
    
    # Campos básicos
    number = models.CharField(max_length=10, unique=True, help_text="Número de habitación")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='individual')
    capacity = models.PositiveIntegerField(default=1, help_text="Número máximo de huéspedes")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio por noche")
    
    # Campos adicionales
    description = models.TextField(blank=True, null=True)
    floor = models.PositiveIntegerField(default=1)
    active = models.BooleanField(default=True, help_text="Si la habitación está disponible para reservas")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Habitación"
        verbose_name_plural = "Habitaciones"
        ordering = ['number']
    
    def __str__(self):
        return f"Habitación {self.number} - {self.get_type_display()}"
    
    @property
    def available_for_booking(self):
        """Verifica si la habitación está disponible para reservas"""
        return self.status == 'available' and self.active
    
    def change_status(self, new_status):
        """Método para cambiar el estado de la habitación"""
        if new_status in dict(self.STATUS_CHOICES):
            self.status = new_status
            self.save()
            return True
        return False
