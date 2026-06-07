from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'worker', 'scheduled_date', 'scheduled_time', 'status', 'payment_status', 'price']
    list_filter = ['status', 'payment_status', 'scheduled_date', 'service_category']
    search_fields = ['title', 'user__username', 'worker__user__username', 'address']
    ordering = ['-scheduled_date', '-created_at']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'scheduled_date'
