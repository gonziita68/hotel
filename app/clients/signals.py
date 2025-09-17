from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Client
import random

@receiver(post_save, sender=User)
def create_client_profile(sender, instance, created, **kwargs):
    """
    Signal para crear automáticamente un perfil de Cliente 
    cuando se crea un nuevo usuario
    """
    if created:
        # Generar email único si no tiene
        email = instance.email
        if not email or Client.objects.filter(email=email).exists():
            email = f'{instance.username}_{random.randint(1000, 9999)}@hotel.com'
        
        try:
            Client.objects.create(
                user=instance,
                first_name=instance.first_name or instance.username,
                last_name=instance.last_name or 'Usuario',
                email=email,
                dni=f'{random.randint(10000000, 99999999)}',  # DNI temporal
                phone=f'+54911{random.randint(1000000, 9999999)}'  # Teléfono temporal
            )
        except Exception as e:
            # Log del error pero no fallar la creación del usuario
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al crear perfil de cliente para usuario {instance.username}: {str(e)}")

@receiver(post_save, sender=User)
def save_client_profile(sender, instance, **kwargs):
    """
    Signal para actualizar el perfil de Cliente cuando se actualiza el usuario
    """
    try:
        client = instance.client
        # Actualizar datos básicos si están vacíos
        if not client.first_name and instance.first_name:
            client.first_name = instance.first_name
        if not client.last_name and instance.last_name:
            client.last_name = instance.last_name
        if not client.email and instance.email:
            client.email = instance.email
        client.save()
    except Client.DoesNotExist:
        # Si no existe el perfil, no hacer nada (se creará en el próximo acceso)
        pass
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al actualizar perfil de cliente para usuario {instance.username}: {str(e)}")