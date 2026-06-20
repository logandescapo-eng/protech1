"""User/worker query services with Redis caching."""

from types import SimpleNamespace

from django.db.models import Q, Sum
from django.utils import timezone

from protech_project.cache_utils import get_cached_categories, get_cached_workers
from protech_project.helpers import user_contact, worker_dict
from .models import Message, ServiceCategory, Worker


def _load_workers(filters):
    qs = Worker.objects.select_related('user').filter(is_available=True)
    if filters.get('skill'):
        qs = qs.filter(skills__icontains=filters['skill'])
    if filters.get('service_area'):
        qs = qs.filter(service_area__icontains=filters['service_area'])
    if filters.get('min_rating'):
        qs = qs.filter(rating__gte=filters['min_rating'])
    if filters.get('category_id'):
        cat = ServiceCategory.objects.filter(pk=filters['category_id']).first()
        if cat:
            qs = qs.filter(skills__icontains=cat.name)
    qs = qs.order_by('-rating', '-total_jobs')
    limit = filters.get('limit')
    if limit:
        qs = qs[: int(limit)]
    return [worker_dict(w) for w in qs]


def get_workers_list(filters=None):
    filters = dict(filters or {})
    if filters.get('category_id'):
        try:
            filters['category_id'] = int(filters['category_id'])
        except (TypeError, ValueError):
            filters.pop('category_id', None)
    return get_cached_workers(filters, lambda: _load_workers(filters))


def get_categories_list():
    def loader():
        return list(ServiceCategory.objects.order_by('name').values('id', 'name', 'description', 'icon'))

    return get_cached_categories(loader)


def get_message_contacts(user):
    """Users the current user has bookings with or prior messages."""
    from bookings.models import Booking
    from django.contrib.auth import get_user_model

    User = get_user_model()
    ids = set()
    if user.user_type == 'worker':
        for b in Booking.objects.filter(worker__user=user).select_related('user'):
            ids.add(b.user_id)
    else:
        for b in Booking.objects.filter(user=user).select_related('worker__user'):
            ids.add(b.worker.user_id)
    for m in Message.objects.filter(Q(sender=user) | Q(receiver=user)):
        ids.add(m.sender_id if m.sender_id != user.id else m.receiver_id)
    ids.discard(user.id)
    contacts = [user_contact(u) for u in User.objects.filter(pk__in=ids)]
    contacts.sort(key=lambda c: c.name.lower())
    return contacts


def get_worker_public_reviews(worker, limit=10):
    from reviews.models import Review

    return Review.objects.filter(worker=worker).select_related('user', 'booking').order_by('-created_at')[:limit]


def get_user_stats(user):
    from reviews.models import Review

    bookings = user.bookings.all()
    active = bookings.filter(status__in=['pending', 'confirmed', 'in_progress']).count()
    completed = bookings.filter(status='completed').count()
    spent = bookings.filter(
        status='completed',
        payment_status__in=['released', 'paid'],
    ).aggregate(total=Sum('price'))['total'] or 0
    return SimpleNamespace(
        active_bookings=active,
        completed_services=completed,
        total_spent=float(spent),
        reviews_given=Review.objects.filter(user=user).count(),
        total_bookings=bookings.count(),
        completed=completed,
        pending=active,
        favorites=user.favorites.count(),
    )


def get_worker_stats(worker):
    first_day = timezone.localdate().replace(day=1)
    bookings = worker.bookings.all()
    monthly = bookings.filter(
        status='completed',
        scheduled_date__gte=first_day,
    ).aggregate(total=Sum('price'))['total'] or 0
    return SimpleNamespace(
        monthly_earnings=float(monthly),
        pending_requests=bookings.filter(status='pending').count(),
        scheduled_jobs=bookings.filter(status__in=['confirmed', 'in_progress']).count(),
        rating=float(worker.rating),
        total_reviews=worker.total_reviews,
        total_jobs=worker.total_jobs,
        completed=bookings.filter(status='completed').count(),
        pending=bookings.filter(status='pending').count(),
    )
