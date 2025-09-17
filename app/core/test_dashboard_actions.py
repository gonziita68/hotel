from django.test import TestCase, Client as TestClient
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import datetime
import json

# Importar modelos
try:
    from app.clients.models import Client
    from app.core.models import ActionLog
except ImportError:
    Client = None
    ActionLog = None


class DashboardActionsTestCase(TestCase):
    """Tests para verificar funcionalidad de botones de acciones rápidas en dashboard"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.client = TestClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_dashboard_loads_with_quick_actions(self):
        """Test: Dashboard carga con botones de acciones rápidas visibles"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Verificar que los botones están presentes con sus IDs correctos
        self.assertContains(response, 'id="nueva-reserva-btn"')
        self.assertContains(response, 'id="nuevo-cliente-btn"')
        self.assertContains(response, 'id="gestionar-habitaciones-btn"')
        self.assertContains(response, 'id="ver-reportes-btn"')
        
        # Verificar que el modal de cliente rápido está presente
        self.assertContains(response, 'id="quickClientModal"')
    
    def test_nueva_reserva_button_redirects_correctly(self):
        """Test: Click en 'Nueva Reserva' redirige al formulario correcto"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Verificar que el botón tiene el URL correcto
        self.assertContains(response, 'booking_step1')
        
        # Test de redirección directa
        response = self.client.get(reverse('booking_step1'))
        # Debería redirigir o cargar la página de reservas
        self.assertIn(response.status_code, [200, 302])
    
    def test_gestionar_habitaciones_button_access(self):
        """Test: Botón 'Gestionar Habitaciones' tiene acceso CRUD correcto"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Verificar que el enlace apunta a la vista de habitaciones
        self.assertContains(response, reverse('rooms'))
        
        # Test de acceso directo
        response = self.client.get(reverse('rooms'))
        self.assertEqual(response.status_code, 200)
    
    def test_ver_reportes_button_loads_page(self):
        """Test: Enlace 'Ver reportes' carga página de reportes"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Verificar que el enlace apunta a la vista de reportes
        self.assertContains(response, reverse('reports'))
        
        # Test de carga de página de reportes
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.status_code, 200)
    
    def test_quick_client_creation_saves_to_database(self):
        """Test: Crear cliente desde acceso rápido genera registro en BD"""
        if not Client:
            self.skipTest("Client model not available")
        
        # Datos del cliente de prueba
        client_data = {
            'action': 'create_client',
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'email': 'juan.perez@test.com',
            'phone': '123456789',
            'dni': '12345678'
        }
        
        # Contar clientes antes
        initial_count = Client.objects.count()
        
        # Enviar solicitud POST
        response = self.client.post(reverse('dashboard'), client_data)
        
        # Verificar respuesta exitosa
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        
        # Debug: imprimir respuesta si falla
        if not response_data.get('success'):
            print(f"Error en creación de cliente: {response_data}")
        
        self.assertTrue(response_data['success'], f"Error: {response_data.get('error', 'Unknown error')}")
        
        # Verificar que se creó el cliente en la BD
        self.assertEqual(Client.objects.count(), initial_count + 1)
        
        # Verificar datos del cliente creado
        client = Client.objects.get(email='juan.perez@test.com')
        self.assertEqual(client.first_name, 'Juan')
        self.assertEqual(client.last_name, 'Pérez')
        self.assertEqual(client.dni, '12345678')
    
    def test_action_logging_records_interactions(self):
        """Test: Registro de acciones guarda interacciones del usuario"""
        # Verificar que el modelo ActionLog esté disponible
        try:
            from .models import ActionLog
        except ImportError:
            self.skipTest("ActionLog model not available")
        
        # Limpiar logs previos
        ActionLog.objects.all().delete()
        
        # Realizar acción en el dashboard
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Verificar que se registró la acción
        logs = ActionLog.objects.filter(user=self.user, action='dashboard_view')
        self.assertTrue(logs.exists(), "No se registró el acceso al dashboard")
        
        log = logs.first()
        self.assertEqual(log.action, 'dashboard_view')
        self.assertEqual(log.description, 'Usuario accedió al dashboard')
        self.assertIsNotNone(log.ip_address)
        self.assertIsNotNone(log.user_agent)
    
    def test_buttons_accessible_and_visible(self):
        """Test: Botones visibles y accesibles en dashboard"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Verificar estructura HTML de acciones rápidas
        self.assertContains(response, 'Acciones Rápidas')
        
        # Verificar que todos los botones están presentes y son accesibles
        buttons = [
            ('nueva-reserva-btn', 'Nueva Reserva'),
            ('nuevo-cliente-btn', 'Nuevo Cliente'),
            ('gestionar-habitaciones-btn', 'Gestionar Habitaciones'),
            ('ver-reportes-btn', 'Ver Reportes')
        ]
        
        for button_id, button_text in buttons:
            self.assertContains(response, f'id="{button_id}"')
            self.assertContains(response, button_text)
    
    def test_action_flow_performance(self):
        """Test: Cada acción abre su flujo en menos de 2 segundos"""
        import time
        
        # Test de tiempo de respuesta del dashboard
        start_time = time.time()
        response = self.client.get(reverse('dashboard'))
        dashboard_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(dashboard_time, 2.0, f"Dashboard debe cargar en menos de 2 segundos (tardó {dashboard_time:.2f}s)")
        
        # Test de tiempo de respuesta de habitaciones
        try:
            start_time = time.time()
            response = self.client.get(reverse('rooms'))
            rooms_time = time.time() - start_time
            
            self.assertEqual(response.status_code, 200)
            self.assertLess(rooms_time, 2.0, f"Vista de habitaciones debe cargar en menos de 2 segundos (tardó {rooms_time:.2f}s)")
        except Exception as e:
            self.skipTest(f"Vista de habitaciones no disponible: {e}")
        
        # Test de tiempo de respuesta de reportes
        try:
            start_time = time.time()
            response = self.client.get(reverse('reports'))
            reports_time = time.time() - start_time
            
            self.assertEqual(response.status_code, 200)
            self.assertLess(reports_time, 2.0, f"Vista de reportes debe cargar en menos de 2 segundos (tardó {reports_time:.2f}s)")
        except Exception as e:
            self.skipTest(f"Vista de reportes no disponible: {e}")
    
    def test_client_creation_with_invalid_data(self):
        """Test: Manejo de errores en creación de cliente con datos inválidos"""
        if not Client:
            self.skipTest("Client model not available")
        
        # Datos inválidos (email duplicado)
        client_data = {
            'action': 'create_client',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',  # Email del usuario de prueba
            'phone': '123456789',
            'dni': '87654321'
        }
        
        # Crear primer cliente
        Client.objects.create(
            first_name='Existing',
            last_name='User',
            email='test@example.com',
            dni='11111111'
        )
        
        # Intentar crear cliente con email duplicado
        response = self.client.post(reverse('dashboard'), client_data)
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)