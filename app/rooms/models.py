from django.db import models
from app.administration.models import Hotel

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
    
    # Hotel
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True, blank=True, help_text="Hotel al que pertenece")
    # Campos básicos
    number = models.CharField(max_length=10, help_text="Número de habitación")
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
        constraints = [
            models.UniqueConstraint(fields=['hotel', 'number'], name='uniq_room_hotel_number')
        ]
    
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
    
    @property
    def main_image(self):
        """Obtiene la imagen principal de la habitación"""
        main_img = self.images.filter(is_main=True).first()
        if main_img:
            return main_img.image.url
        # Si no hay imagen principal, tomar la primera disponible
        first_img = self.images.first()
        if first_img:
            return first_img.image.url
        # Imagen por defecto si no hay ninguna
        return "https://images.unsplash.com/photo-1566665797739-1674de7a421a?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80"
    
    @property
    def all_images(self):
        """Obtiene todas las imágenes de la habitación ordenadas"""
        return self.images.all().order_by('-is_main', 'order', 'id')


class RoomImage(models.Model):
    """
    Modelo para las imágenes de las habitaciones
    """
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='rooms/', help_text="Imagen de la habitación")
    alt_text = models.CharField(max_length=200, blank=True, help_text="Texto alternativo para la imagen")
    is_main = models.BooleanField(default=False, help_text="Imagen principal de la habitación")
    order = models.PositiveIntegerField(default=0, help_text="Orden de visualización")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Imagen de Habitación"
        verbose_name_plural = "Imágenes de Habitaciones"
        ordering = ['-is_main', 'order', 'id']
    
    def __str__(self):
        main_text = " (Principal)" if self.is_main else ""
        return f"Imagen de {self.room.number}{main_text}"
    
    def save(self, *args, **kwargs):
        # Si esta imagen se marca como principal, desmarcar las demás
        if self.is_main:
            RoomImage.objects.filter(room=self.room, is_main=True).update(is_main=False)
