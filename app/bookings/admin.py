from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Booking
    """
    list_display = ['id', 'client', 'room', 'check_in_date', 'check_out_date', 'status', 'payment_status', 'total_price']
    list_filter = ['status', 'payment_status', 'check_in_date', 'created_at']
    search_fields = ['client__first_name', 'client__last_name', 'client__email', 'room__number']
    list_editable = ['status', 'payment_status']
    readonly_fields = ['created_at', 'updated_at', 'confirmed_at', 'cancelled_at']
    
    fieldsets = (
        ('Información de la Reserva', {
            'fields': ('client', 'room', 'check_in_date', 'check_out_date', 'guests_count')
        }),
        ('Estado y Pagos', {
            'fields': ('status', 'payment_status', 'total_price')
        }),
        ('Información Adicional', {
            'fields': ('special_requests', 'cancellation_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimizar consultas con select_related"""
        return super().get_queryset(request).select_related('client', 'room')
    
    def duration_days(self, obj):
        """Método para mostrar duración de la reserva"""
        return obj.duration
    duration_days.short_description = 'Días'
    
    def is_active_booking(self, obj):
        """Método para mostrar si la reserva está activa"""
        return obj.is_active
    is_active_booking.boolean = True
    is_active_booking.short_description = 'Activa'
    
    actions = ['confirm_bookings', 'cancel_bookings']
    
    def confirm_bookings(self, request, queryset):
        """Acción para confirmar múltiples reservas"""
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f'{updated} reservas fueron confirmadas.')
    confirm_bookings.short_description = "Confirmar reservas seleccionadas"
    
    def cancel_bookings(self, request, queryset):
        """Acción para cancelar múltiples reservas"""
        updated = queryset.filter(status__in=['pending', 'confirmed']).update(status='cancelled')
        self.message_user(request, f'{updated} reservas fueron canceladas.')
    cancel_bookings.short_description = "Cancelar reservas seleccionadas"
