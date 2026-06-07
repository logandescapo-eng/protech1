from django.db import models
from django.core.validators import MinValueValidator

class UserWallet(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='wallet')
    available_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_wallets'
    
    def __str__(self):
        return f"Wallet for {self.user.username} - ${self.available_balance}"


class EscrowVault(models.Model):
    id = models.IntegerField(primary_key=True)
    total_held = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    total_released = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'escrow_vault'
    
    def __str__(self):
        return f"Escrow Vault - Held: ${self.total_held}, Released: ${self.total_released}"
    
    def save(self, *args, **kwargs):
        self.id = 1
        super().save(*args, **kwargs)


class EscrowHold(models.Model):
    STATUS_CHOICES = [
        ('held', 'Held'),
        ('released', 'Released'),
        ('refunded', 'Refunded'),
    ]
    
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='escrow_hold')
    client = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='escrow_holds_as_client')
    worker_user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='escrow_holds_as_worker')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    platform_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    worker_payout = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='held')
    created_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'escrow_holds'
        indexes = [
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Escrow for booking {self.booking.id} - ${self.amount} ({self.status})"


class WalletTransaction(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='wallet_transactions')
    booking = models.ForeignKey('bookings.Booking', on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    escrow = models.ForeignKey(EscrowHold, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    transaction_type = models.CharField(max_length=32)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'wallet_transactions'
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} - {self.user.username}: ${self.amount}"
