"""Template context shared across the ProTech UI."""

from django.conf import settings
from django.urls import reverse

from users.models import Favorite, Message, Notification


def _initials(name):
    parts = (name or 'U').split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return (name or 'U')[:2].upper()


def layout_context(request):
    ctx = {
        'is_logged_in': request.user.is_authenticated,
        'platform_fee_percent': settings.ESCROW_PLATFORM_FEE_PERCENT,
        'layout_unread_notifications': 0,
        'layout_unread_messages': 0,
        'layout_user_type': None,
        'layout_dashboard_url': reverse('index'),
    }
    if request.user.is_authenticated:
        ctx['layout_dashboard_url'] = (
            reverse('worker_dashboard')
            if request.user.user_type == 'worker'
            else reverse('user_dashboard')
        )
        ctx['layout_user_type'] = request.user.user_type
        ctx['layout_unread_notifications'] = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
        ctx['layout_unread_messages'] = Message.objects.filter(
            receiver=request.user, is_read=False
        ).count()
    return ctx
