from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ActionLog(models.Model):
    """Modelo para registrar acciones del usuario en el sistema"""
    
    ACTION_CHOICES = [
        ('nueva_reserva', 'Nueva Reserva'),
        ('nuevo_cliente', 'Nuevo Cliente'),
        ('gestionar_habitaciones', 'Gestionar Habitaciones'),
        ('ver_reportes', 'Ver Reportes'),
        ('dashboard_view', 'Vista Dashboard'),
    ]
    
    # Información de la acción
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, verbose_name="Acción")
    description = models.CharField(max_length=200, blank=True, verbose_name="Descripción")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Dirección IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    
    class Meta:
        verbose_name = "Log de Acción"
        verbose_name_plural = "Logs de Acciones"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.created_at}"

class EmailLog(models.Model):
    """Modelo para registrar emails enviados del sistema"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('sent', 'Enviado'),
        ('failed', 'Fallido'),
    ]
    
    # Información del email
    recipient_email = models.EmailField(verbose_name="Email del destinatario")
    recipient_name = models.CharField(max_length=100, blank=True, verbose_name="Nombre del destinatario")
    subject = models.CharField(max_length=200, verbose_name="Asunto")
    content = models.TextField(verbose_name="Contenido del email")
    
    # Estado y tracking
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending', 
        verbose_name="Estado"
    )
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de envío")
    error_message = models.TextField(blank=True, verbose_name="Mensaje de error")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    
    # Relaciones opcionales para tracking
    booking = models.ForeignKey(
        'bookings.Booking', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Reserva relacionada"
    )
    client = models.ForeignKey(
        'clients.Client', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Cliente relacionado"
    )

    class Meta:
        verbose_name = "Registro de Email"
        verbose_name_plural = "Registros de Email"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['recipient_email']),
        ]

    def __str__(self):
        return f"{self.recipient_email} - {self.subject} ({self.get_status_display()})"
    
    def mark_as_sent(self):
        """Marca el email como enviado"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at'])
    
    def mark_as_failed(self, error_message=""):
        """Marca el email como fallido"""
        self.status = 'failed'
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message'])
