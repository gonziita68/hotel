import os
from django.core.asgi import get_asgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = get_asgi_application()

try:
    call_command('init_db')
except Exception:
    pass
