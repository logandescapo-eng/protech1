from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['booking', 'user', 'worker', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'worker__user__username', 'comment']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
