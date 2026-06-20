"""Template context shared across the ProTech UI."""

from django.conf import settings
from django.urls import reverse

from protech_project.helpers import display_name, initials
from users.models import Message, Notification
from users.services import get_message_contacts


def _active_page(request):
    path = request.path.rstrip('/') or '/'
    if path.startswith('/bookings'):
        view = request.GET.get('view')
        if view == 'pending':
            return 'job_requests'
        if view == 'schedule':
            return 'schedule'
        return 'bookings'
    rules = (
        ('/user/dashboard', 'dashboard'),
        ('/worker/dashboard', 'dashboard'),
        ('/workers', 'browse'),
        ('/book', 'browse'),
        ('/wallet', 'wallet'),
        ('/messages', 'messages'),
        ('/reviews', 'reviews'),
        ('/review', 'reviews'),
        ('/favorites', 'favorites'),
        ('/notifications', 'notifications'),
        ('/profile', 'profile'),
        ('/settings', 'settings'),
        ('/booking', 'bookings'),
    )
    for prefix, key in rules:
        if path == prefix or path.startswith(prefix + '/'):
            return key
    return ''


def layout_context(request):
    ctx = {
        'is_logged_in': request.user.is_authenticated,
        'platform_fee_percent': settings.ESCROW_PLATFORM_FEE_PERCENT,
        'layout_unread_notifications': 0,
        'layout_unread_messages': 0,
        'layout_user_type': None,
        'layout_user_name': '',
        'layout_initials': '',
        'layout_active_page': '',
        'layout_dashboard_url': reverse('index'),
        'layout_notifications': [],
        'layout_message_contacts': [],
    }
    if request.user.is_authenticated:
        name = display_name(request.user)
        ctx['layout_dashboard_url'] = (
            reverse('worker_dashboard')
            if request.user.user_type == 'worker'
            else reverse('user_dashboard')
        )
        ctx['layout_user_type'] = request.user.user_type
        ctx['layout_user_name'] = name
        ctx['layout_initials'] = initials(name)
        ctx['layout_active_page'] = _active_page(request)
        ctx['layout_unread_notifications'] = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
        ctx['layout_unread_messages'] = Message.objects.filter(
            receiver=request.user, is_read=False
        ).count()
        ctx['layout_notifications'] = list(
            Notification.objects.filter(user=request.user).order_by('-created_at')[:8]
        )
        ctx['layout_message_contacts'] = get_message_contacts(request.user)
    return ctx
