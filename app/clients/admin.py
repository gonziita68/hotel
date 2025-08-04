from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Client
    """
    list_display = ['full_name', 'email', 'phone', 'dni', 'active', 'vip']
    list_filter = ['active', 'vip', 'nationality', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'dni', 'phone']
    list_editable = ['active', 'vip']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'dni')
        }),
        ('Información Adicional', {
            'fields': ('address', 'birth_date', 'nationality')
        }),
        ('Estado', {
            'fields': ('active', 'vip')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request)
    
    def booking_count(self, obj):
        """Método para mostrar cantidad de reservas del cliente"""
        return obj.booking_set.count()
    booking_count.short_description = 'Reservas'
