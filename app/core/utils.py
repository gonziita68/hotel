from .models import ActionLog
from django.contrib.auth.models import User

def log_user_action(user, action, description="", request=None):
    """
    Función utilitaria para registrar acciones del usuario
    
    Args:
        user: Usuario que realiza la acción
        action: Tipo de acción (debe estar en ACTION_CHOICES)
        description: Descripción opcional de la acción
        request: Request object para obtener IP y User-Agent
    """
    ip_address = None
    user_agent = ""
    
    if request:
        # Obtener IP del usuario
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Obtener User-Agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Crear el log
    ActionLog.objects.create(
        user=user,
        action=action,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent
    )