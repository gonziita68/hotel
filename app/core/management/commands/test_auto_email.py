from django.core.management.base import BaseCommand
from app.core.services import EmailService
from app.bookings.models import Booking
from app.clients.models import Client
from app.rooms.models import Room
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Prueba el envío automático de emails al crear reservas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--client-id',
            type=int,
            help='ID del cliente para crear la reserva de prueba'
        )
        parser.add_argument(
            '--room-id',
            type=int,
            help='ID de la habitación para la reserva de prueba'
        )
        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='Crear datos de prueba si no existen'
        )

    def handle(self, *args, **options):
        client_id = options['client_id']
        room_id = options['room_id']
        create_test_data = options['create_test_data']

        if create_test_data:
            self.create_test_data()
            return

        if not client_id or not room_id:
            self.stdout.write(
                self.style.ERROR('Debes especificar --client-id y --room-id, o usar --create-test-data')
            )
            return

        self.test_automatic_email(client_id, room_id)

    def create_test_data(self):
        """Crea datos de prueba para testing"""
        try:
            # Crear cliente de prueba
            client, created = Client.objects.get_or_create(
                email='test@example.com',
                defaults={
                    'first_name': 'Juan',
                    'last_name': 'Pérez',
                    'phone': '+1234567890',
                    'dni': '12345678'
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Cliente de prueba creado: {client.full_name} (ID: {client.id})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Cliente de prueba ya existe: {client.full_name} (ID: {client.id})')
                )

            # Crear habitación de prueba
            room, created = Room.objects.get_or_create(
                number='TEST-001',
                defaults={
                    'type': 'standard',
                    'capacity': 2,
                    'price': 100.00,
                    'status': 'available'
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Habitación de prueba creada: {room.number} (ID: {room.id})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Habitación de prueba ya existe: {room.number} (ID: {room.id})')
                )

            self.stdout.write(
                self.style.SUCCESS('\n📋 Datos de prueba creados. Usa:')
            )
            self.stdout.write(
                f'   python manage.py test_auto_email --client-id {client.id} --room-id {room.id}'
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al crear datos de prueba: {str(e)}')
            )

    def test_automatic_email(self, client_id, room_id):
        """Prueba el envío automático de email al crear una reserva"""
        try:
            # Verificar que existen los objetos
            client = Client.objects.get(id=client_id)
            room = Room.objects.get(id=room_id)
            
            self.stdout.write(
                self.style.SUCCESS(f'🧪 Probando envío automático de email...')
            )
            self.stdout.write(f'   - Cliente: {client.full_name} ({client.email})')
            self.stdout.write(f'   - Habitación: {room.number}')
            
            # Fechas de prueba (mañana y pasado mañana)
            tomorrow = date.today() + timedelta(days=1)
            day_after_tomorrow = date.today() + timedelta(days=2)
            
            # Crear reserva (esto debería disparar el email automáticamente)
            booking = Booking.objects.create(
                client=client,
                room=room,
                check_in_date=tomorrow,
                check_out_date=day_after_tomorrow,
                status='confirmed',
                payment_status='pending',
                guests_count=2,
                special_requests='Reserva de prueba para testing de emails',
                total_price=room.price * 1  # 1 día
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Reserva creada exitosamente: #{booking.id}')
            )
            self.stdout.write(f'   - Fechas: {tomorrow} a {day_after_tomorrow}')
            self.stdout.write(f'   - Precio: ${booking.total_price}')
            
            # Verificar si se creó el log de email
            from app.core.models import EmailLog
            email_logs = EmailLog.objects.filter(booking=booking).order_by('-created_at')
            
            if email_logs.exists():
                latest_log = email_logs.first()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Log de email creado: #{latest_log.id}')
                )
                self.stdout.write(f'   - Estado: {latest_log.status}')
                self.stdout.write(f'   - Destinatario: {latest_log.recipient_email}')
                
                if latest_log.status == 'sent':
                    self.stdout.write(
                        self.style.SUCCESS('🎉 ¡Email enviado automáticamente!')
                    )
                elif latest_log.status == 'failed':
                    self.stdout.write(
                        self.style.ERROR(f'❌ Email falló: {latest_log.error_message}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️ Email en estado: {latest_log.status}')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️ No se encontró log de email')
                )
            
            # Limpiar reserva de prueba
            booking.delete()
            self.stdout.write(
                self.style.SUCCESS('🧹 Reserva de prueba eliminada')
            )
                
        except Client.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Cliente #{client_id} no encontrado')
            )
        except Room.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Habitación #{room_id} no encontrada')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error inesperado: {str(e)}')
            ) 