from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Worker, ServiceCategory, Message, Notification, Favorite, WorkerAvailability


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'user_type', 'phone', 'is_staff', 'created_at']
    list_filter = ['user_type', 'is_staff', 'is_superuser', 'created_at']
    search_fields = ['username', 'email', 'phone']
    ordering = ['-created_at']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone', 'avatar')}),
    )


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ['user', 'service_area', 'hourly_rate', 'rating', 'total_reviews', 'total_jobs', 'is_available']
    list_filter = ['is_available', 'created_at']
    search_fields = ['user__username', 'service_area', 'skills']
    ordering = ['-rating', '-total_reviews']
    readonly_fields = ['rating', 'total_reviews', 'total_jobs']


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'booking', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'receiver__username', 'message']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'type', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'worker', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'worker__user__username']
    ordering = ['-created_at']


@admin.register(WorkerAvailability)
class WorkerAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['worker', 'day_of_week', 'start_time', 'end_time', 'is_available']
    list_filter = ['day_of_week', 'is_available']
    search_fields = ['worker__user__username']
    ordering = ['worker', 'day_of_week']
