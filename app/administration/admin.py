from django.contrib import admin
from .models import Hotel


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "email_contact", "phone")
    search_fields = ("name", "slug", "email_contact", "phone")

# Register your models here.
