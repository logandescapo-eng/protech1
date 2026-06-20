import logging

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from bookings.models import Booking
from django.contrib.auth.decorators import login_required

from users.decorators import user_type_required
from users.models import Worker

from .models import Review

logger = logging.getLogger(__name__)


@login_required
@user_type_required('user')
def review(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related('worker__user'),
        pk=booking_id,
        user=request.user,
        status='completed',
    )
    if Review.objects.filter(booking=booking).exists():
        messages.info(request, 'You already reviewed this booking')
        return redirect('my_bookings')
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        Review.objects.create(
            booking=booking,
            user=request.user,
            worker=booking.worker,
            rating=rating,
            comment=comment,
        )
        worker = booking.worker
        reviews = Review.objects.filter(worker=worker)
        worker.total_reviews = reviews.count()
        worker.rating = sum(r.rating for r in reviews) / max(worker.total_reviews, 1)
        worker.save(update_fields=['total_reviews', 'rating', 'updated_at'])
        from protech_project.cache_utils import invalidate_workers_cache

        invalidate_workers_cache()
        logger.info('Review created for booking %s', booking_id)
        messages.success(request, 'Thank you for your review!')
        return redirect('my_bookings')
    return render(request, 'review.html', {
        'booking': booking,
        'page_title': 'Leave a Review',
    })
