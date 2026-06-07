"""User/worker query services with Redis caching."""

from protech_project.cache_utils import get_cached_categories, get_cached_workers
from protech_project.helpers import worker_dict
from .models import ServiceCategory, Worker


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


def get_worker_public_reviews(worker, limit=10):
    from reviews.models import Review

    return Review.objects.filter(worker=worker).select_related('user', 'booking').order_by('-created_at')[:limit]


def get_user_stats(user):
    bookings = user.bookings.all()
    return {
        'total_bookings': bookings.count(),
        'completed': bookings.filter(status='completed').count(),
        'pending': bookings.filter(status__in=['pending', 'confirmed', 'in_progress']).count(),
        'favorites': user.favorites.count(),
    }


def get_worker_stats(worker):
    bookings = worker.bookings.all()
    return {
        'total_jobs': bookings.count(),
        'completed': bookings.filter(status='completed').count(),
        'pending': bookings.filter(status='pending').count(),
        'rating': float(worker.rating),
        'total_reviews': worker.total_reviews,
    }
