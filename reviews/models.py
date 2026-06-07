from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='review')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reviews_given')
    worker = models.ForeignKey('users.Worker', on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reviews'
        indexes = [
            models.Index(fields=['worker']),
        ]
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.worker.user.username} - {self.rating}/5"
