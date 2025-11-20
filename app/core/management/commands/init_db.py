from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
import os
from app.administration.models import Hotel

class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command('migrate', interactive=False)
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        if username and email and password:
            User = get_user_model()
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username=username, email=email, password=password)
        # Crear hotel demo si no existe
        if not Hotel.objects.filter(slug='demo').exists():
            Hotel.objects.create(
                name='Hotel Demo',
                slug='demo',
                email_contact=os.environ.get('DEMO_HOTEL_EMAIL', ''),
                phone=os.environ.get('DEMO_HOTEL_PHONE', ''),
                address=os.environ.get('DEMO_HOTEL_ADDRESS', 'Demo Address')
            )
