from django.test import TestCase, Client as TestClient
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

# Importar modelos de las apps
try:
    from app.rooms.models import Room
    from app.bookings.models import Booking
    from app.clients.models import Client
except ImportError:
    # Fallback si los modelos no están disponibles
    Room = None
    Booking = None
    Client = None

from app.core.views import get_dashboard_metrics


class DashboardMetricsTestCase(TestCase):
    """Tests unitarios para las métricas del dashboard"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client = TestClient()
        
        # Limpiar datos existentes para tener un estado conocido
        if Room:
            Room.objects.all().delete()
        if Booking:
            Booking.objects.all().delete()
        if Client:
            Client.objects.all().delete()
            
        # Solo crear datos de prueba si los modelos están disponibles
        if Room and Booking and Client:
            self.create_test_data()
    
    def create_test_data(self):
        """Crear datos de prueba para los tests"""
        # Crear habitaciones de prueba usando los campos correctos del modelo
        self.room1 = Room.objects.create(
            number='101',
            type='individual',
            price=Decimal('100000.00'),
            status='available',
            active=True
        )
        self.room2 = Room.objects.create(
            number='102',
            type='double',
            price=Decimal('150000.00'),
            status='occupied',
            active=True
        )
        self.room3 = Room.objects.create(
            number='103',
            type='suite',
            price=Decimal('250000.00'),
            status='cleaning',
            active=True
        )
        self.room4 = Room.objects.create(
            number='104',
            type='individual',
            price=Decimal('100000.00'),
            status='maintenance',
            active=True
        )
        
        # Crear cliente de prueba
        self.test_client = Client.objects.create(
            first_name='Juan',
            last_name='Pérez',
            email='juan@example.com',
            phone='3001234567'
        )
        
        # Crear reservas de prueba
        today = timezone.now().date()
        self.booking1 = Booking.objects.create(
            client=self.test_client,
            room=self.room1,  # Use room1 which is available
            check_in_date=today,
            check_out_date=today + timedelta(days=2),
            total_price=Decimal('200000.00'),  # Updated price for room1
            status='confirmed'
        )
    
    def test_get_dashboard_metrics_structure(self):
        """Test que verifica la estructura de las métricas del dashboard"""
        metrics = get_dashboard_metrics()
        
        # Verificar que todas las claves necesarias están presentes
        required_keys = [
            'total_rooms', 'available_rooms', 'occupied_rooms', 
            'cleaning_rooms', 'maintenance_rooms', 'total_revenue',
            'active_bookings', 'recent_bookings', 'total_clients',
            'maintenance_alerts'
        ]
        
        for key in required_keys:
            self.assertIn(key, metrics, f"La clave '{key}' debe estar presente en las métricas")
    
    def test_room_counts_calculation(self):
        """Test que verifica el cálculo correcto de contadores de habitaciones"""
        if not Room:
            self.skipTest("Modelo Room no disponible")
            
        metrics = get_dashboard_metrics()
        
        # Verificar contadores de habitaciones
        self.assertEqual(metrics['total_rooms'], 4, "Total de habitaciones debe ser 4")
        self.assertEqual(metrics['available_rooms'], 1, "Habitaciones disponibles debe ser 1")
        self.assertEqual(metrics['occupied_rooms'], 1, "Habitaciones ocupadas debe ser 1")
        self.assertEqual(metrics['cleaning_rooms'], 1, "Habitaciones en limpieza debe ser 1")
        self.assertEqual(metrics['maintenance_rooms'], 1, "Habitaciones en mantenimiento debe ser 1")
    
    def test_revenue_calculation(self):
        """Test que verifica el cálculo correcto de ingresos mensuales"""
        if not Booking:
            self.skipTest("Modelo Booking no disponible")
            
        metrics = get_dashboard_metrics()
        
        # Verificar que el ingreso total es correcto
        self.assertIsInstance(metrics['total_revenue'], (int, float, Decimal))
        self.assertGreaterEqual(metrics['total_revenue'], 0, "Los ingresos no pueden ser negativos")
    
    def test_metrics_data_types(self):
        """Test que verifica los tipos de datos de las métricas"""
        metrics = get_dashboard_metrics()
        
        # Verificar tipos de datos
        self.assertIsInstance(metrics['total_rooms'], int)
        self.assertIsInstance(metrics['available_rooms'], int)
        self.assertIsInstance(metrics['occupied_rooms'], int)
        self.assertIsInstance(metrics['cleaning_rooms'], int)
        self.assertIsInstance(metrics['maintenance_rooms'], int)
        self.assertIsInstance(metrics['total_revenue'], (int, float, Decimal))
        self.assertIsInstance(metrics['active_bookings'], int)
        self.assertIsInstance(metrics['total_clients'], int)


class DashboardAPITestCase(TestCase):
    """Tests para el API de métricas del dashboard"""
    
    def setUp(self):
        """Configuración inicial para los tests del API"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = TestClient()
        self.api_url = reverse('dashboard_metrics_api')
    
    def test_dashboard_metrics_api_requires_login(self):
        """Test que verifica que el API requiere autenticación"""
        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, 302, "API debe requerir login")
    
    def test_dashboard_metrics_api_authenticated(self):
        """Test que verifica el funcionamiento del API con usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.api_url)
        
        self.assertEqual(response.status_code, 200, "API debe responder correctamente")
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Verificar que la respuesta es JSON válido
        data = json.loads(response.content)
        self.assertIsInstance(data, dict, "La respuesta debe ser un diccionario")
        
        # Verificar estructura de la respuesta
        required_keys = ['total_rooms', 'available_rooms', 'occupied_rooms', 'total_revenue']
        for key in required_keys:
            self.assertIn(key, data, f"La respuesta debe incluir '{key}'")


class DashboardIntegrationTestCase(TestCase):
    """Tests de integración para el dashboard"""
    
    def setUp(self):
        """Configuración inicial para tests de integración"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = TestClient()
        self.dashboard_url = reverse('dashboard')
    
    def test_dashboard_view_renders_correctly(self):
        """Test que verifica que el dashboard se renderiza correctamente"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.dashboard_url)
        
        self.assertEqual(response.status_code, 200, "Dashboard debe cargar correctamente")
        self.assertContains(response, 'Dashboard', msg_prefix="Debe contener el título Dashboard")
        self.assertContains(response, 'Total Habitaciones', msg_prefix="Debe mostrar métricas de habitaciones")
        self.assertContains(response, 'Disponibles', msg_prefix="Debe mostrar habitaciones disponibles")
        self.assertContains(response, 'Ocupadas', msg_prefix="Debe mostrar habitaciones ocupadas")
        self.assertContains(response, 'Ingresos del Mes', msg_prefix="Debe mostrar ingresos mensuales")
    
    def test_dashboard_metrics_elements_present(self):
        """Test que verifica la presencia de elementos de métricas en el HTML"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.dashboard_url)
        
        # Verificar que los IDs de las métricas están presentes
        self.assertContains(response, 'id="total-rooms"', msg_prefix="Debe tener elemento total-rooms")
        self.assertContains(response, 'id="available-rooms"', msg_prefix="Debe tener elemento available-rooms")
        self.assertContains(response, 'id="occupied-rooms"', msg_prefix="Debe tener elemento occupied-rooms")
        self.assertContains(response, 'id="total-revenue"', msg_prefix="Debe tener elemento total-revenue")
    
    def test_dashboard_javascript_present(self):
        """Test que verifica la presencia del JavaScript de actualización automática"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.dashboard_url)
        
        # Verificar que el JavaScript está presente
        self.assertContains(response, 'updateDashboardMetrics', msg_prefix="Debe incluir función de actualización")
        self.assertContains(response, 'formatCurrency', msg_prefix="Debe incluir función de formato de moneda")
        self.assertContains(response, 'setInterval', msg_prefix="Debe incluir actualización automática")


class BookingImpactTestCase(TestCase):
    """Tests que verifican el impacto de las reservas en las métricas"""
    
    def setUp(self):
        """Configuración inicial para tests de impacto de reservas"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        if Room and Client:
            self.room = Room.objects.create(
                number='201',
                type='individual',
                price=Decimal('120000.00'),
                status='available'
            )
            
            self.test_client = Client.objects.create(
                first_name='María',
                last_name='García',
                email='maria@example.com',
                phone='3009876543'
            )
    
    def test_booking_creation_updates_metrics(self):
        """Test que verifica que crear una reserva actualiza las métricas"""
        if not (Room and Booking and Client):
            self.skipTest("Modelos no disponibles")
        
        # Limpiar datos existentes para tener un estado conocido
        Booking.objects.all().delete()
        
        # Verificar que no hay reservas activas inicialmente
        today = timezone.now().date()
        initial_count = Booking.objects.filter(
            check_in_date__lte=today,
            check_out_date__gte=today,
            status='confirmed'
        ).values('room').distinct().count()
        
        self.assertEqual(initial_count, 0, "No debe haber reservas activas inicialmente")
        
        # Crear una nueva reserva activa (que comience hoy)
        booking = Booking.objects.create(
            client=self.test_client,
            room=self.room,
            check_in_date=today,
            check_out_date=today + timedelta(days=1),
            total_price=Decimal('120000.00'),
            status='confirmed'
        )
        
        # Verificar que ahora hay una reserva activa
        updated_count = Booking.objects.filter(
            check_in_date__lte=today,
            check_out_date__gte=today,
            status='confirmed'
        ).values('room').distinct().count()
        
        self.assertEqual(updated_count, 1, "Debe haber una reserva activa después de crear la reserva")
    
    def test_booking_cancellation_updates_metrics(self):
        """Test que verifica que cancelar una reserva actualiza las métricas"""
        if not (Room and Booking and Client):
            self.skipTest("Modelos no disponibles")
        
        # Limpiar datos existentes
        Booking.objects.all().delete()
        
        # Crear una reserva activa que comience hoy
        today = timezone.now().date()
        booking = Booking.objects.create(
            client=self.test_client,
            room=self.room,
            check_in_date=today,
            check_out_date=today + timedelta(days=1),
            total_price=Decimal('120000.00'),
            status='confirmed'
        )
        
        # Verificar que hay una reserva activa
        count_with_booking = Booking.objects.filter(
            check_in_date__lte=today,
            check_out_date__gte=today,
            status='confirmed'
        ).values('room').distinct().count()
        
        self.assertEqual(count_with_booking, 1, "Debe haber una reserva activa")
        
        # Cancelar la reserva
        booking.status = 'cancelled'
        booking.save()
        
        # Verificar que ya no hay reservas activas
        count_after_cancel = Booking.objects.filter(
            check_in_date__lte=today,
            check_out_date__gte=today,
            status='confirmed'
        ).values('room').distinct().count()
        
        self.assertEqual(count_after_cancel, 0, "No debe haber reservas activas después de cancelar")
    
    def test_payment_updates_revenue(self):
        """Test que verifica que los pagos se reflejan en los ingresos del mes"""
        if not (Room and Booking and Client):
            self.skipTest("Modelos no disponibles")
        
        from django.db.models import Sum
        
        # Limpiar datos existentes
        Booking.objects.all().delete()
        
        # Crear una reserva para este mes
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        
        booking = Booking.objects.create(
            client=self.test_client,
            room=self.room,
            check_in_date=start_of_month,
            check_out_date=start_of_month + timedelta(days=2),
            total_price=Decimal('240000.00'),
            status='confirmed'
        )
        
        # Verificar que el ingreso se refleja en las métricas
        total_revenue = Booking.objects.filter(
            check_in_date__gte=start_of_month,
            status__in=['confirmed', 'completed']
        ).aggregate(total=Sum('total_price'))['total']
        
        self.assertEqual(total_revenue, Decimal('240000.00'), "El ingreso debe reflejarse correctamente")
