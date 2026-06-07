import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from bookings.models import Booking

from . import services
from .models import WalletTransaction

logger = logging.getLogger(__name__)


@login_required
def wallet_page(request):
    if request.method == 'POST':
        try:
            amount = request.POST.get('amount', '50')
            services.deposit_demo_funds(request.user, amount)
            messages.success(request, f'Added ${amount} demo funds to your wallet')
        except ValueError as exc:
            messages.error(request, str(exc))
        return redirect('wallet_page')

    wallet = services.get_wallet_summary(request.user)
    transactions = WalletTransaction.objects.filter(user=request.user).order_by('-created_at')[:30]
    vault = services.get_vault_summary()
    return render(request, 'wallet.html', {
        'wallet': wallet,
        'transactions': transactions,
        'vault': vault,
        'platform_fee_percent': settings.ESCROW_PLATFORM_FEE_PERCENT,
    })


@login_required
def escrow_pay(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related('worker__user', 'user'),
        pk=booking_id,
        user=request.user,
    )
    wallet = services.get_wallet_summary(request.user)
    if request.method == 'POST':
        try:
            services.fund_escrow(booking, request.user)
            from users.models import Notification
            from protech_project.email_notify import notify_user_email
            from protech_project.helpers import display_name

            msg = f'{display_name(request.user)} funded escrow (${booking.price}) for "{booking.title}".'
            Notification.objects.create(
                user=booking.worker.user,
                title='Escrow funded',
                message=msg,
                type='booking',
                link=f'/booking/{booking.id}/',
            )
            notify_user_email(booking.worker.user, 'Escrow funded', msg)
            messages.success(request, 'Payment moved to escrow successfully')
            return redirect('booking_detail', booking_id=booking.id)
        except (ValueError, PermissionError) as exc:
            messages.error(request, str(exc))
    return render(request, 'escrow_pay.html', {
        'booking': booking,
        'wallet': wallet,
        'platform_fee_percent': settings.ESCROW_PLATFORM_FEE_PERCENT,
    })
