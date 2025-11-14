from django import forms
from django.core.exceptions import ValidationError
from .models import Room, RoomImage

class RoomForm(forms.ModelForm):
    """Formulario para crear y editar habitaciones"""
    
    class Meta:
        model = Room
        fields = ['number', 'type', 'capacity', 'floor', 'price', 'status', 'description', 'active']
        widgets = {
            'number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 101, 201A, Suite 1'
            }),
            'type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            }),
            'floor': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 20
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción opcional de la habitación...'
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'number': 'Número de Habitación',
            'type': 'Tipo de Habitación',
            'capacity': 'Capacidad (personas)',
            'floor': 'Piso',
            'price': 'Precio por Noche',
            'status': 'Estado',
            'description': 'Descripción',
            'active': 'Habitación Activa'
        }
        help_texts = {
            'number': 'Número único que identifica la habitación',
            'capacity': 'Número máximo de huéspedes',
            'price': 'Precio en pesos colombianos',
            'description': 'Información adicional sobre amenidades, vista, etc.'
        }

    def clean_number(self):
        """Validar que el número de habitación sea único"""
        number = self.cleaned_data.get('number')
        if not number:
            raise ValidationError('El número de habitación es requerido.')
        
        # Verificar unicidad
        queryset = Room.objects.filter(number=number)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise ValidationError(f'Ya existe una habitación con el número "{number}".')
        
        return number

    def clean_capacity(self):
        """Validar capacidad"""
        capacity = self.cleaned_data.get('capacity')
        if capacity and capacity < 1:
            raise ValidationError('La capacidad debe ser al menos 1 persona.')
        if capacity and capacity > 10:
            raise ValidationError('La capacidad no puede ser mayor a 10 personas.')
        return capacity

    def clean_floor(self):
        """Validar piso"""
        floor = self.cleaned_data.get('floor')
        if floor and floor < 1:
            raise ValidationError('El piso debe ser al menos 1.')
        if floor and floor > 20:
            raise ValidationError('El piso no puede ser mayor a 20.')
        return floor

    def clean_price(self):
        """Validar precio"""
        price = self.cleaned_data.get('price')
        if price and price < 0:
            raise ValidationError('El precio no puede ser negativo.')
        if price and price > 10000000:  # 10 millones
            raise ValidationError('El precio no puede ser mayor a $10,000,000.')
        return price

    def clean(self):
        """Validaciones adicionales del formulario"""
        cleaned_data = super().clean()
        room_type = cleaned_data.get('type')
        capacity = cleaned_data.get('capacity')
        
        # Validar capacidad según tipo de habitación
        if room_type and capacity:
            type_capacity_map = {
                'individual': (1, 1),
                'double': (1, 2),
                'triple': (2, 3),
                'suite': (2, 4),
                'family': (3, 6)
            }
            
            if room_type in type_capacity_map:
                min_cap, max_cap = type_capacity_map[room_type]
                if capacity < min_cap or capacity > max_cap:
                    raise ValidationError(
                        f'Para habitaciones tipo "{room_type}", la capacidad debe estar entre {min_cap} y {max_cap} personas.'
                    )
        
        return cleaned_data

class RoomImageForm(forms.ModelForm):
    """Formulario para subir imágenes de habitaciones"""
    
    class Meta:
        model = RoomImage
        fields = ['image', 'alt_text', 'is_main']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Texto alternativo (opcional)'
            }),
            'is_main': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'image': 'Imagen',
            'alt_text': 'Texto alternativo',
            'is_main': 'Imagen Principal'
        }

    def clean_image(self):
        """Validar imagen"""
        image = self.cleaned_data.get('image')
        if image:
            # Validar tamaño (máximo 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('La imagen no puede ser mayor a 5MB.')
            
            # Validar tipo de archivo
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if hasattr(image, 'content_type') and image.content_type not in allowed_types:
                raise ValidationError('Solo se permiten imágenes en formato JPEG, PNG o WebP.')
        
        return image

class RoomFilterForm(forms.Form):
    """Formulario para filtrar habitaciones"""
    
    status = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Room.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    type = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + Room.TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    floor = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Piso',
            'min': 1,
            'max': 20
        })
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por número o descripción...'
        })
    )
    
    min_price = forms.DecimalField(
        required=False,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Precio mínimo',
            'step': '0.01'
        })
    )
    
    max_price = forms.DecimalField(
        required=False,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Precio máximo',
            'step': '0.01'
        })
    )

class BulkRoomStatusForm(forms.Form):
    """Formulario para actualizar el estado de múltiples habitaciones"""
    
    room_ids = forms.CharField(widget=forms.HiddenInput())
    new_status = forms.ChoiceField(
        choices=Room.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def clean_room_ids(self):
        """Validar IDs de habitaciones"""
        room_ids_str = self.cleaned_data.get('room_ids')
        if not room_ids_str:
            raise ValidationError('No se seleccionaron habitaciones.')
        
        try:
            room_ids = [int(id.strip()) for id in room_ids_str.split(',') if id.strip()]
        except ValueError:
            raise ValidationError('IDs de habitaciones inválidos.')
        
        if not room_ids:
            raise ValidationError('No se seleccionaron habitaciones válidas.')
        
        # Verificar que las habitaciones existan
        existing_rooms = Room.objects.filter(id__in=room_ids).count()
        if existing_rooms != len(room_ids):
            raise ValidationError('Algunas habitaciones seleccionadas no existen.')
        
        return room_ids