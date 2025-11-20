from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import hashlib

from app.administration.models import Hotel
from app.rooms.models import Room
from app.bookings.models import Booking
from app.clients.models import Client


class Command(BaseCommand):
    help = "Seed de datos coherentes para Hotel O11CE y Hotel Demo (multi-hotel) relativo a hoy"

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Limpiar bookings del rango antes de crear')

    @transaction.atomic
    def handle(self, *args, **options):
        today = timezone.now().date()
        start = today - timedelta(days=19)
        end = today + timedelta(days=5)

        self.stdout.write(self.style.NOTICE(f"Sembrando datos relativos a hoy={today} (rango {start} → {end})"))

        # Crear/obtener hoteles
        o11ce, _ = Hotel.objects.get_or_create(
            slug='o11ce',
            defaults={
                'name': 'Hotel O11CE',
                'email_contact': 'reservas@hotelo11ce.com',
                'phone': '+54 351 445-0011',
                'address': 'Av. General Paz 1123, Córdoba Capital',
            },
        )
        demo, _ = Hotel.objects.get_or_create(
            slug='demo-mini',
            defaults={
                'name': 'Hotel Demo',
                'email_contact': 'reservas@demo.com',
                'phone': '+54 351 000-0000',
                'address': 'Calle Ficticia 123, Córdoba',
            },
        )

        # Crear habitaciones O11CE si no existen (40 total)
        type_price = {
            'individual': 80,
            'double': 120,
            'triple': 160,
            'suite': 220,
        }

        def ensure_room(hotel, number, floor, type_key, capacity):
            room, created = Room.objects.get_or_create(
                hotel=hotel, number=str(number),
                defaults={
                    'type': type_key,
                    'capacity': capacity,
                    'status': 'available',
                    'price': type_price[type_key],
                    'floor': floor,
                    'active': True,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Room creada {hotel.slug} #{number}"))
            return room

        # 101–110 single
        for n in range(101, 111):
            ensure_room(o11ce, n, 1, 'individual', 1)
        # 201–215 double
        for n in range(201, 216):
            ensure_room(o11ce, n, 2, 'double', 2)
        # 301–310 triple
        for n in range(301, 311):
            ensure_room(o11ce, n, 3, 'triple', 3)
        # 401–405 suite
        for n in range(401, 406):
            ensure_room(o11ce, n, 4, 'suite', 3)

        # Crear habitaciones demo (5)
        for n in range(501, 506):
            ensure_room(demo, n, 5, 'double', 2)

        # Idempotencia: limpiar bookings del rango SOLO de O11CE si --reset
        if options.get('reset'):
            deleted = Booking.objects.filter(hotel=o11ce, check_in_date__gte=start, check_in_date__lte=end).delete()[0]
            # Reset status de rooms O11CE
            Room.objects.filter(hotel=o11ce).update(status='available', active=True)
            self.stdout.write(self.style.WARNING(f"Bookings O11CE en rango eliminados: {deleted}"))

        # Helpers clientes
        def ensure_client(email, first_name, last_name, hotel):
            seed = f"{email}|{hotel.slug}"
            base = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16)
            dni_num = 10000000 + (base % 90000000)
            client, _ = Client.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': '',
                    'dni': str(dni_num),
                    'hotel': hotel,
                },
            )
            if client.hotel_id != hotel.id:
                client.hotel = hotel
                client.save(update_fields=['hotel'])
            return client

        # Crear bloque de ocupación hoy: 25 rooms confirmadas solapando hoy
        occupy_rooms_numbers = list(range(101, 111)) + list(range(201, 211)) + list(range(301, 306))  # 10 + 10 + 5 = 25
        for idx, num in enumerate(occupy_rooms_numbers, start=1):
            room = Room.objects.get(hotel=o11ce, number=str(num))
            client = ensure_client(f"ocupacion{idx}@o11ce.test", f"Cliente{idx}", "Ocupacion", o11ce)
            Booking.objects.create(
                hotel=o11ce,
                client=client,
                room=room,
                check_in_date=today - timedelta(days=2),
                check_out_date=today + timedelta(days=2),
                status='confirmed',
                payment_status='paid',
                paid_amount=room.price * 2,  # parcial, no importa exacto
                guests_count=min(room.capacity, 2),
                total_price=room.price * 4,
            )
            room.change_status('occupied')

        # Tres check-in hoy: pending, confirmed, cancelled
        for mark, st in enumerate(['confirmed', 'pending', 'cancelled'], start=1):
            num = 306 + mark  # 307, 308, 309
            room = Room.objects.get(hotel=o11ce, number=str(num))
            client = ensure_client(f"checkin{mark}@o11ce.test", f"Checkin{mark}", "Hoy", o11ce)
            Booking.objects.create(
                hotel=o11ce,
                client=client,
                room=room,
                check_in_date=today,
                check_out_date=today + timedelta(days=2),
                status=st,
                payment_status='pending',
                paid_amount=0,
                guests_count=min(room.capacity, 2),
                total_price=room.price * 2,
            )
            if st == 'confirmed':
                room.change_status('occupied')
            elif st == 'pending':
                room.change_status('reserved')
            elif st == 'cancelled':
                room.change_status('available')

        # Reservas de primeros días (distribución)
        early_cases = [
            (101, start + timedelta(days=1), start + timedelta(days=4), 'confirmed', 'Juan', 'Perez'),
            (102, start + timedelta(days=2), start + timedelta(days=3), 'cancelled', 'Maria', 'Lopez'),
            (201, start + timedelta(days=4), start + timedelta(days=7), 'confirmed', 'Carlos', 'Ruiz'),
            (202, start + timedelta(days=6), start + timedelta(days=9), 'confirmed', 'TechCor', 'SA'),
            (203, start + timedelta(days=8), start + timedelta(days=10), 'pending', 'Ana', 'Gomez'),
        ]
        for num, ci, co, st, fn, ln in early_cases:
            room = Room.objects.get(hotel=o11ce, number=str(num))
            client = ensure_client(f"early{num}@o11ce.test", fn, ln, o11ce)
            Booking.objects.create(
                hotel=o11ce, client=client, room=room,
                check_in_date=ci, check_out_date=co, status=st,
                payment_status='pending', paid_amount=0,
                guests_count=min(room.capacity, 2), total_price=room.price * max((co - ci).days, 1)
            )

        # Reservas mitad de mes
        mid_cases = [
            (204, start + timedelta(days=11), start + timedelta(days=14), 'confirmed', 'Pedro', 'Sanchez'),
            (205, start + timedelta(days=12), start + timedelta(days=15), 'cancelled', 'Lucia', 'Martinez'),
            (206, start + timedelta(days=13), start + timedelta(days=16), 'confirmed', 'Corp', 'Booking'),
        ]
        for num, ci, co, st, fn, ln in mid_cases:
            room = Room.objects.get(hotel=o11ce, number=str(num))
            client = ensure_client(f"mid{num}@o11ce.test", fn, ln, o11ce)
            Booking.objects.create(
                hotel=o11ce, client=client, room=room,
                check_in_date=ci, check_out_date=co, status=st,
                payment_status='pending', paid_amount=0,
                guests_count=min(room.capacity, 2), total_price=room.price * max((co - ci).days, 1)
            )

        # Reserva futura cancelada
        room401 = Room.objects.get(hotel=o11ce, number='401')
        client401 = ensure_client("future401@o11ce.test", "Futuro", "Cancel", o11ce)
        Booking.objects.create(
            hotel=o11ce, client=client401, room=room401,
            check_in_date=today + timedelta(days=5), check_out_date=today + timedelta(days=8),
            status='cancelled', payment_status='pending', paid_amount=0,
            guests_count=min(room401.capacity, 2), total_price=room401.price * 3
        )

        # Hotel Demo: 5 rooms, 3 bookings
        demo_rooms = list(Room.objects.filter(hotel=demo).order_by('number'))
        if demo_rooms:
            dclient1 = ensure_client("demo1@demo.test", "Demo", "Uno", demo)
            dclient2 = ensure_client("demo2@demo.test", "Demo", "Dos", demo)
            dclient3 = ensure_client("demo3@demo.test", "Demo", "Tres", demo)
            Booking.objects.create(hotel=demo, client=dclient1, room=demo_rooms[0],
                                   check_in_date=start + timedelta(days=10), check_out_date=start + timedelta(days=12),
                                   status='confirmed', payment_status='paid', paid_amount=demo_rooms[0].price*2,
                                   guests_count=2, total_price=demo_rooms[0].price*2)
            Booking.objects.create(hotel=demo, client=dclient2, room=demo_rooms[1],
                                   check_in_date=start + timedelta(days=12), check_out_date=start + timedelta(days=13),
                                   status='cancelled', payment_status='pending', paid_amount=0,
                                   guests_count=2, total_price=demo_rooms[1].price)
            Booking.objects.create(hotel=demo, client=dclient3, room=demo_rooms[2],
                                   check_in_date=today, check_out_date=today + timedelta(days=1),
                                   status='pending', payment_status='pending', paid_amount=0,
                                   guests_count=2, total_price=demo_rooms[2].price)

        self.stdout.write(self.style.SUCCESS("Seed O11CE + Demo completado"))