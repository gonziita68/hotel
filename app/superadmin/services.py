from typing import Optional, Dict, Any
from datetime import date
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from app.bookings.models import Booking
from app.rooms.models import Room
from app.administration.models import Hotel


def get_dashboard_data(scope: str, hotel: Optional[Hotel], desde: date, hasta: date) -> Dict[str, Any]:
    bookings_qs = Booking.objects.filter(check_in_date__range=(desde, hasta))
    rooms_qs = Room.objects.all()
    if scope == "hotel" and hotel is not None:
        bookings_qs = bookings_qs.filter(hotel=hotel)
        rooms_qs = rooms_qs.filter(hotel=hotel)
    today = timezone.now().date()
    active_today_qs = Booking.objects.filter(check_in_date__lte=today, check_out_date__gt=today, status="confirmed")
    if scope == "hotel" and hotel is not None:
        active_today_qs = active_today_qs.filter(hotel=hotel)
    occupied_rooms_count = active_today_qs.values("room").distinct().count()
    total_rooms = rooms_qs.count()
    occupancy_today = None if total_rooms == 0 else occupied_rooms_count / total_rooms
    checkin_qs = Booking.objects.filter(check_in_date=today)
    if scope == "hotel" and hotel is not None:
        checkin_qs = checkin_qs.filter(hotel=hotel)
    bookings_checkin_today_total = checkin_qs.count()
    reservations_period_count = bookings_qs.count()
    daily = bookings_qs.annotate(d=TruncDate("check_in_date")).values("d", "status").annotate(count=Count("id")).order_by("d")
    daily_map: Dict[str, Dict[str, int]] = {}
    for row in daily:
        d = row["d"].isoformat()
        s = row["status"]
        c = row["count"]
        if d not in daily_map:
            daily_map[d] = {"pending": 0, "confirmed": 0, "cancelled": 0}
        if s in daily_map[d]:
            daily_map[d][s] += c
    daily_bookings = [{"date": d, **daily_map[d]} for d in sorted(daily_map.keys())]
    status_counts = bookings_qs.values("status").annotate(count=Count("id"))
    status_dist = {"pending": 0, "confirmed": 0, "cancelled": 0}
    for row in status_counts:
        s = row["status"]
        c = row["count"]
        if s in status_dist:
            status_dist[s] = c
    return {
        "kpis": {
            "occupancy_today": occupancy_today,
            "bookings_checkin_today_total": bookings_checkin_today_total,
            "reservations_period_count": reservations_period_count,
        },
        "series": {"daily_bookings": daily_bookings},
        "distributions": {"status": status_dist},
    }