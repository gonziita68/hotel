from django.apps import AppConfig


class ClientsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.clients'
    
    def ready(self):
        import app.clients.signals
