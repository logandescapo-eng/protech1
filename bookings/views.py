import logging
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from protech_project.email_notify import notify_user_email
from protech_project.helpers import booking_dict, display_name, worker_dict

from users.decorators import user_type_required
from users.models import Notification, ServiceCategory, Worker
from users.availability import check_slot_available

from .models import Booking

logger = logging.getLogger(__name__)

BOOKING_RELATED = ('user', 'worker__user', 'service_category', 'escrow_hold')


def _notify_booking(booking, recipient, title, message, link='/bookings/'):
    Notification.objects.create(
        user=recipient,
        title=title,
        message=message,
        type='booking',
        link=link,
    )
    notify_user_email(
        recipient,
        title,
        f'{message}\n\nView: {link}',
    )


def _booking_queryset_for(user):
    qs = Booking.objects.select_related(*BOOKING_RELATED)
    if user.user_type == 'worker':
        return qs.filter(worker__user=user)
    return qs.filter(user=user)


@login_required
def my_bookings(request):
    user = request.user
    qs = _booking_queryset_for(user).order_by('-created_at')
    bookings = [booking_dict(b) for b in qs]
    pending_review_ids = set()
    if user.user_type == 'user':
        from reviews.models import Review

        pending_review_ids = set(
            Booking.objects.filter(user=user, status='completed')
            .exclude(id__in=Review.objects.filter(user=user).values_list('booking_id', flat=True))
            .values_list('id', flat=True)
        )
    from escrow.services import get_wallet_summary

    wallet = get_wallet_summary(user)
    return render(request, 'my_bookings.html', {
        'bookings': bookings,
        'user_type': user.user_type,
        'pending_review_ids': pending_review_ids,
        'wallet': wallet,
    })


@login_required
def booking_detail(request, booking_id):
    user = request.user
    booking = get_object_or_404(
        Booking.objects.select_related(*BOOKING_RELATED),
        pk=booking_id,
    )
    if user.user_type == 'worker' and booking.worker.user_id != user.id:
        messages.error(request, 'Permission denied')
        return redirect('my_bookings')
    if user.user_type == 'user' and booking.user_id != user.id:
        messages.error(request, 'Permission denied')
        return redirect('my_bookings')

    b = booking_dict(booking)
    from reviews.models import Review

    has_review = Review.objects.filter(booking=booking).exists()
    other_user = booking.worker.user if user.user_type == 'user' else booking.user
    return render(request, 'booking_detail.html', {
        'booking': b,
        'user_type': user.user_type,
        'has_review': has_review,
        'other_user_id': other_user.id,
        'other_user_name': display_name(other_user),
    })


@login_required
@user_type_required('user')
def book_worker(request, worker_id):
    from django.conf import settings

    worker = get_object_or_404(Worker.objects.select_related('user'), pk=worker_id)
    w = worker_dict(worker)
    categories = list(
        ServiceCategory.objects.order_by('name').values('id', 'name', 'description', 'icon')
    )
    if request.method == 'POST':
        try:
            scheduled_date = datetime.strptime(
                request.POST.get('scheduled_date', ''), '%Y-%m-%d'
            ).date()
            scheduled_time = datetime.strptime(
                request.POST.get('scheduled_time', ''), '%H:%M'
            ).time()
            ok, msg = check_slot_available(worker, scheduled_date, scheduled_time)
            if not ok:
                messages.error(request, msg)
                return redirect('book_worker', worker_id=worker_id)

            price = request.POST.get('price') or worker.hourly_rate
            category_id = request.POST.get('service_category_id') or None
            service_category = None
            if category_id:
                service_category = ServiceCategory.objects.filter(pk=category_id).first()

            booking = Booking.objects.create(
                user=request.user,
                worker=worker,
                service_category=service_category,
                title=request.POST.get('title', f'Service with {w.name}'),
                description=request.POST.get('description', ''),
                scheduled_date=scheduled_date,
                scheduled_time=scheduled_time,
                estimated_duration=int(request.POST.get('estimated_duration') or 60),
                address=request.POST.get('address', worker.service_area),
                price=price,
                status='pending',
            )
            detail_url = f'/booking/{booking.id}/'
            _notify_booking(
                booking,
                worker.user,
                'New booking request',
                f'{display_name(request.user)} requested "{booking.title}" on {scheduled_date}.',
                link=detail_url,
            )
            logger.info('Booking %s created by user %s', booking.id, request.user.id)
            messages.success(request, 'Booking created! Fund escrow when ready.')
            return redirect('booking_detail', booking_id=booking.id)
        except (ValueError, TypeError) as exc:
            logger.error('Booking creation failed: %s', exc)
            messages.error(request, 'Could not create booking — check date, time, and price.')
    return render(request, 'book_worker.html', {
        'worker': w,
        'categories': categories,
        'platform_fee_percent': settings.ESCROW_PLATFORM_FEE_PERCENT,
    })


def _escrow_is_held(booking):
    try:
        return booking.escrow_hold.status == 'held'
    except Exception:
        return booking.payment_status == 'escrow_held'


@login_required
def update_booking(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related('worker__user', 'user', 'escrow_hold'),
        pk=booking_id,
    )
    user = request.user
    if user.user_type == 'worker' and booking.worker.user_id != user.id:
        messages.error(request, 'Permission denied')
        return redirect('my_bookings')
    if user.user_type == 'user' and booking.user_id != user.id:
        messages.error(request, 'Permission denied')
        return redirect('my_bookings')

    action = request.POST.get('action')
    detail = redirect('booking_detail', booking_id=booking_id)
    try:
        if action in ('confirm', 'accept') and user.user_type == 'worker':
            booking.status = 'confirmed'
            booking.save(update_fields=['status', 'updated_at'])
            _notify_booking(
                booking, booking.user, 'Booking accepted',
                f'{display_name(user)} accepted your booking "{booking.title}".',
                link=f'/booking/{booking.id}/',
            )
        elif action == 'decline' and user.user_type == 'worker':
            booking.status = 'cancelled'
            booking.save(update_fields=['status', 'updated_at'])
            _notify_booking(
                booking, booking.user, 'Booking declined',
                f'Your booking "{booking.title}" was declined.',
                link=f'/booking/{booking.id}/',
            )
        elif action == 'start' and user.user_type == 'worker':
            if not _escrow_is_held(booking):
                messages.error(
                    request,
                    'Client must fund escrow before work can start.',
                )
                return detail
            booking.status = 'in_progress'
            booking.save(update_fields=['status', 'updated_at'])
            _notify_booking(
                booking, booking.user, 'Work started',
                f'Work has started on "{booking.title}".',
                link=f'/booking/{booking.id}/',
            )
        elif action == 'complete' and user.user_type == 'worker':
            from escrow.services import release_escrow

            booking.status = 'completed'
            if _escrow_is_held(booking):
                release_escrow(booking)
            else:
                booking.save(update_fields=['status', 'updated_at'])
            _notify_booking(
                booking, booking.user, 'Job completed',
                f'"{booking.title}" is marked complete. Escrow released to the worker.',
                link=f'/booking/{booking.id}/',
            )
        elif action == 'cancel':
            refunded = False
            try:
                if booking.escrow_hold.status == 'held':
                    from escrow.services import refund_escrow

                    refund_escrow(booking)
                    refunded = True
            except Exception:
                pass
            if not refunded:
                booking.status = 'cancelled'
                booking.save(update_fields=['status', 'updated_at'])
            other = booking.worker.user if user.user_type == 'user' else booking.user
            _notify_booking(
                booking, other, 'Booking cancelled',
                f'Booking "{booking.title}" was cancelled.',
                link=f'/booking/{booking.id}/',
            )
        else:
            messages.error(request, 'Unknown action')
            return detail
        logger.info('Booking %s action %s by %s', booking_id, action, user.id)
        messages.success(request, 'Booking updated')
    except Exception as exc:
        logger.error('Booking update failed: %s', exc)
        messages.error(request, str(exc))
    return detail
