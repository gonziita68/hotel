from django.contrib import admin
from .models import Room

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Room
    """
    list_display = ['number', 'type', 'status', 'price', 'capacity', 'floor', 'active']
    list_filter = ['type', 'status', 'floor', 'active']
    search_fields = ['number', 'description']
    list_editable = ['status', 'price', 'active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('number', 'type', 'capacity', 'price', 'status')
        }),
        ('Detalles', {
            'fields': ('description', 'floor', 'active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimizar consultas con select_related"""
        return super().get_queryset(request)
    
    def available_rooms(self, obj):
        """Método para mostrar habitaciones disponibles"""
        return obj.available_for_booking
    available_rooms.boolean = True
    available_rooms.short_description = 'Disponible'
