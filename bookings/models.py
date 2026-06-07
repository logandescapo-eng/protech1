from django.db import models
from django.core.validators import MinValueValidator

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('escrow_held', 'Escrow Held'),
        ('released', 'Released'),
        ('refunded', 'Refunded'),
        ('paid', 'Paid'),
    ]
    
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='bookings')
    worker = models.ForeignKey('users.Worker', on_delete=models.CASCADE, related_name='bookings')
    service_category = models.ForeignKey('users.ServiceCategory', on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    estimated_duration = models.IntegerField(default=60, validators=[MinValueValidator(1)])
    address = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bookings'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['worker']),
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_date']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username} -> {self.worker.user.username}"
