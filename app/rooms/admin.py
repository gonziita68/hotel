from django.contrib import admin
from django.utils.html import format_html
from .models import Room, RoomImage


class RoomImageInline(admin.TabularInline):
    """
    Inline admin para gestionar imágenes de habitaciones
    """
    model = RoomImage
    extra = 1
    fields = ['image', 'alt_text', 'is_main', 'order', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        """Muestra una vista previa de la imagen"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px; border-radius: 5px;" />',
                obj.image.url
            )
        return "Sin imagen"
    image_preview.short_description = "Vista Previa"


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Room
    """
    list_display = ['number', 'type', 'status', 'price', 'capacity', 'floor', 'active', 'image_count', 'available_rooms']
    list_filter = ['type', 'status', 'floor', 'active']
    search_fields = ['number', 'description']
    list_editable = ['status', 'price', 'active']
    readonly_fields = ['created_at', 'updated_at', 'main_image_preview']
    inlines = [RoomImageInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('number', 'type', 'capacity', 'price', 'status')
        }),
        ('Detalles', {
            'fields': ('description', 'floor', 'active')
        }),
        ('Imagen Principal', {
            'fields': ('main_image_preview',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimizar consultas con prefetch_related para imágenes"""
        return super().get_queryset(request).prefetch_related('images')
    
    def available_rooms(self, obj):
        """Método para mostrar habitaciones disponibles"""
        return obj.available_for_booking
    available_rooms.boolean = True
    available_rooms.short_description = 'Disponible'
    
    def image_count(self, obj):
        """Muestra el número de imágenes de la habitación"""
        count = obj.images.count()
        if count == 0:
            return format_html('<span style="color: red;">0 imágenes</span>')
        elif count == 1:
            return format_html('<span style="color: orange;">1 imagen</span>')
        else:
            return format_html('<span style="color: green;">{} imágenes</span>', count)
    image_count.short_description = 'Imágenes'
    
    def main_image_preview(self, obj):
        """Muestra la imagen principal de la habitación"""
        main_img = obj.images.filter(is_main=True).first()
        if main_img and main_img.image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 300px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                main_img.image.url
            )
        elif obj.images.exists():
            first_img = obj.images.first()
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 300px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" /><br><small style="color: orange;">Primera imagen (no marcada como principal)</small>',
                first_img.image.url
            )
        return format_html('<div style="padding: 20px; background: #f8f9fa; border-radius: 10px; text-align: center; color: #6c757d;">Sin imágenes</div>')
    main_image_preview.short_description = 'Imagen Principal'


@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    """
    Admin para gestionar imágenes de habitaciones individualmente
    """
    list_display = ['room', 'alt_text', 'is_main', 'order', 'image_preview', 'created_at']
    list_filter = ['is_main', 'room__type', 'created_at']
    search_fields = ['room__number', 'alt_text']
    list_editable = ['is_main', 'order']
    readonly_fields = ['image_preview', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('room', 'image', 'alt_text')
        }),
        ('Configuración', {
            'fields': ('is_main', 'order')
        }),
        ('Vista Previa', {
            'fields': ('image_preview',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        """Muestra una vista previa de la imagen"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 300px; max-width: 400px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return "Sin imagen"
    image_preview.short_description = "Vista Previa"
