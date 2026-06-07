from django.contrib import admin
from .models import UserWallet, EscrowVault, EscrowHold, WalletTransaction


@admin.register(UserWallet)
class UserWalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'available_balance', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['updated_at']


@admin.register(EscrowVault)
class EscrowVaultAdmin(admin.ModelAdmin):
    list_display = ['id', 'total_held', 'total_released', 'updated_at']
    readonly_fields = ['id', 'total_held', 'total_released', 'updated_at']


@admin.register(EscrowHold)
class EscrowHoldAdmin(admin.ModelAdmin):
    list_display = ['booking', 'client', 'worker_user', 'amount', 'platform_fee', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['booking__id', 'client__username', 'worker_user__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'released_at']


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'amount', 'balance_after', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['user__username', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
