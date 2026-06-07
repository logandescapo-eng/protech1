"""Escrow ledger service (Django ORM)."""

from decimal import Decimal, ROUND_HALF_UP
import logging

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from bookings.models import Booking
from .models import EscrowHold, EscrowVault, UserWallet, WalletTransaction

logger = logging.getLogger(__name__)

PLATFORM_FEE_RATE = Decimal(str(settings.ESCROW_PLATFORM_FEE_PERCENT)) / Decimal('100')
DEMO_DEPOSIT_MAX = Decimal('500.00')


def _money(value):
    return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def ensure_wallet(user):
    wallet, _ = UserWallet.objects.get_or_create(user=user)
    wallet.available_balance = _money(wallet.available_balance)
    return wallet


def get_wallet_summary(user):
    wallet = ensure_wallet(user)
    return {
        'user_id': user.id,
        'available_balance': wallet.available_balance,
        'updated_at': wallet.updated_at,
    }


def get_vault_summary():
    vault, _ = EscrowVault.objects.get_or_create(pk=1, defaults={'id': 1})
    return {'total_held': vault.total_held, 'total_released': vault.total_released}


@transaction.atomic
def deposit_demo_funds(user, amount):
    amount = _money(amount)
    if amount <= 0 or amount > DEMO_DEPOSIT_MAX:
        raise ValueError('Invalid deposit amount')
    wallet = ensure_wallet(user)
    wallet.available_balance = _money(wallet.available_balance) + amount
    wallet.save(update_fields=['available_balance', 'updated_at'])
    WalletTransaction.objects.create(
        user=user,
        transaction_type='deposit',
        amount=amount,
        balance_after=wallet.available_balance,
        description='Demo bank deposit',
    )
    logger.info('Demo deposit %s for user %s', amount, user.id)
    return wallet


@transaction.atomic
def fund_escrow(booking, client):
    if booking.user_id != client.id:
        raise PermissionError('Not your booking')
    if hasattr(booking, 'escrow_hold'):
        raise ValueError('Escrow already funded')
    amount = _money(booking.price)
    wallet = ensure_wallet(client)
    if wallet.available_balance < amount:
        raise ValueError('Insufficient wallet balance')
    wallet.available_balance = _money(wallet.available_balance) - amount
    wallet.save(update_fields=['available_balance', 'updated_at'])
    fee = _money(amount * PLATFORM_FEE_RATE)
    payout = amount - fee
    hold = EscrowHold.objects.create(
        booking=booking,
        client=client,
        worker_user=booking.worker.user,
        amount=amount,
        platform_fee=fee,
        worker_payout=payout,
        status='held',
    )
    vault, _ = EscrowVault.objects.select_for_update().get_or_create(pk=1, defaults={'id': 1})
    vault.total_held = _money(vault.total_held) + amount
    vault.save(update_fields=['total_held', 'updated_at'])
    booking.payment_status = 'escrow_held'
    booking.save(update_fields=['payment_status', 'updated_at'])
    WalletTransaction.objects.create(
        user=client,
        booking=booking,
        escrow=hold,
        transaction_type='escrow_fund',
        amount=-amount,
        balance_after=wallet.available_balance,
        description=f'Escrow for {booking.title}',
    )
    logger.info('Escrow funded booking %s amount %s', booking.id, amount)
    return hold


@transaction.atomic
def release_escrow(booking):
    hold = EscrowHold.objects.select_for_update().get(booking=booking, status='held')
    worker_wallet = ensure_wallet(hold.worker_user)
    payout = _money(hold.worker_payout or (hold.amount - hold.platform_fee))
    worker_wallet.available_balance = _money(worker_wallet.available_balance) + payout
    worker_wallet.save(update_fields=['available_balance', 'updated_at'])
    hold.status = 'released'
    hold.released_at = timezone.now()
    hold.save()
    vault = EscrowVault.objects.select_for_update().get(pk=1)
    vault.total_held = _money(vault.total_held) - _money(hold.amount)
    vault.total_released = _money(vault.total_released) + payout
    vault.save()
    booking.payment_status = 'released'
    booking.status = 'completed'
    booking.save(update_fields=['payment_status', 'status', 'updated_at'])
    WalletTransaction.objects.create(
        user=hold.worker_user,
        booking=booking,
        escrow=hold,
        transaction_type='escrow_release',
        amount=payout,
        balance_after=worker_wallet.available_balance,
        description=f'Payment for {booking.title}',
    )
    logger.info('Escrow released booking %s', booking.id)


@transaction.atomic
def refund_escrow(booking):
    hold = EscrowHold.objects.select_for_update().get(booking=booking, status='held')
    client_wallet = ensure_wallet(hold.client)
    amount = _money(hold.amount)
    client_wallet.available_balance = _money(client_wallet.available_balance) + amount
    client_wallet.save(update_fields=['available_balance', 'updated_at'])
    hold.status = 'refunded'
    hold.released_at = timezone.now()
    hold.save()
    vault = EscrowVault.objects.select_for_update().get(pk=1)
    vault.total_held = _money(vault.total_held) - amount
    vault.save()
    booking.payment_status = 'refunded'
    booking.status = 'cancelled'
    booking.save(update_fields=['payment_status', 'status', 'updated_at'])
    WalletTransaction.objects.create(
        user=hold.client,
        booking=booking,
        escrow=hold,
        transaction_type='escrow_refund',
        amount=amount,
        balance_after=client_wallet.available_balance,
        description=f'Refund for {booking.title}',
    )
    logger.info('Escrow refunded booking %s', booking.id)
