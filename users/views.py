import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from bookings.models import Booking
from protech_project.helpers import booking_dict, display_name, initials, user_contact, worker_dict
from reviews.models import Review

from .availability import get_worker_availability, save_worker_availability
from .decorators import user_type_required
from .models import Favorite, Message, Notification, Worker
from .services import (
    get_categories_list,
    get_user_stats,
    get_worker_public_reviews,
    get_worker_stats,
    get_workers_list,
)

logger = logging.getLogger(__name__)


def _render_landing(request, title, subtitle, content_template, cta_label=None, cta_url=None):
    return render(request, 'landing/page.html', {
        'page_title': title,
        'page_subtitle': subtitle,
        'content_template': content_template,
        'cta_label': cta_label,
        'cta_url': cta_url,
    })


def home(request):
    logger.info('Home page accessed')
    return render(request, 'index.html')


def auth_view(request):
    if request.user.is_authenticated:
        return redirect('worker_dashboard' if request.user.user_type == 'worker' else 'user_dashboard')

    if request.method == 'POST':
        if 'login' in request.POST:
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Login successful!')
                logger.info('User %s logged in', email)
                return redirect('worker_dashboard' if user.user_type == 'worker' else 'user_dashboard')
            messages.error(request, 'Invalid email or password')
            logger.warning('Failed login for %s', email)
            return redirect('auth')

        if 'user_signup' in request.POST:
            return _register_client(request)
        if 'worker_signup' in request.POST:
            return _register_worker(request)

    tab = request.GET.get('tab', 'login')
    return render(request, 'auth.html', {'active_tab': tab})


def _register_client(request):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip().lower()
    phone = request.POST.get('phone', '').strip()
    password = request.POST.get('password', '')
    if not all([name, email, phone, password]):
        messages.error(request, 'Please fill in all fields')
        return redirect('auth')
    if User.objects.filter(email__iexact=email).exists():
        messages.error(request, 'Email already registered')
        return redirect('auth')
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=name,
        phone=phone,
        user_type='user',
    )
    logger.info('Registered client %s', email)
    messages.success(request, 'Registration successful! Please login.')
    return redirect('auth')


def _register_worker(request):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip().lower()
    phone = request.POST.get('phone', '').strip()
    password = request.POST.get('password', '')
    service_area = request.POST.get('address', '').strip()
    skills = request.POST.get('skills', '').strip()
    try:
        experience = int(request.POST.get('experience') or 0)
    except (TypeError, ValueError):
        experience = 0
    if not all([name, email, phone, password, service_area, skills]):
        messages.error(request, 'Please fill in all fields')
        return redirect('auth')
    if User.objects.filter(email__iexact=email).exists():
        messages.error(request, 'Email already registered')
        return redirect('auth')
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=name,
        phone=phone,
        user_type='worker',
    )
    Worker.objects.create(
        user=user,
        service_area=service_area,
        skills=skills,
        experience=experience,
    )
    logger.info('Registered worker %s', email)
    messages.success(request, 'Worker registration successful! Please login.')
    return redirect('auth')


def logout_view(request):
    logger.info('User %s logged out', request.user)
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('index')


@login_required
@user_type_required('user')
def user_dashboard(request):
    user = request.user
    name = display_name(user)
    upcoming = [
        booking_dict(b) for b in user.bookings.filter(
            status__in=['pending', 'confirmed', 'in_progress']
        ).select_related('worker__user')[:5]
    ]
    pending_reviews = [
        booking_dict(b) for b in user.bookings.filter(status='completed').exclude(
            id__in=Review.objects.filter(user=user).values_list('booking_id', flat=True)
        )[:10]
    ]
    pending_review_ids = {b.id for b in pending_reviews}
    recent_completed = [
        booking_dict(b) for b in user.bookings.filter(status='completed').select_related('worker__user')[:5]
    ]
    return render(request, 'user.html', {
        'user_name': name,
        'stats': get_user_stats(user),
        'upcoming_bookings': upcoming,
        'pending_reviews': pending_reviews,
        'pending_review_ids': pending_review_ids,
        'recent_completed': recent_completed,
        'initials': initials(name),
        'unread_notifications': Notification.objects.filter(user=user, is_read=False).count(),
        'unread_messages': Message.objects.filter(receiver=user, is_read=False).count(),
    })


@login_required
@user_type_required('worker')
def worker_dashboard(request):
    user = request.user
    try:
        worker = Worker.objects.select_related('user').get(user=user)
    except Worker.DoesNotExist:
        messages.error(request, 'Worker profile not found')
        return redirect('logout')
    name = display_name(user)
    w = worker_dict(worker)
    pending = [booking_dict(b) for b in worker.bookings.filter(status='pending').select_related('user')[:5]]
    today = timezone.localdate()
    today_schedule = [
        booking_dict(b) for b in worker.bookings.filter(scheduled_date=today)
        .exclude(status='cancelled')
        .select_related('user').order_by('scheduled_time')
    ]
    completed = [booking_dict(b) for b in worker.bookings.filter(status='completed').select_related('user')[:5]]
    return render(request, 'worker.html', {
        'user_name': name,
        'worker': w,
        'stats': get_worker_stats(worker),
        'pending_requests': pending,
        'today_schedule': today_schedule,
        'recent_completed': completed,
        'unread_notifications': Notification.objects.filter(user=user, is_read=False).count(),
        'unread_messages': Message.objects.filter(receiver=user, is_read=False).count(),
        'initials': initials(name),
    })


@login_required
@user_type_required('user')
def browse_workers(request):
    filters = {'limit': 20}
    if request.GET.get('skill'):
        filters['skill'] = request.GET.get('skill')
    if request.GET.get('location'):
        filters['service_area'] = request.GET.get('location')
    if request.GET.get('min_rating'):
        try:
            filters['min_rating'] = float(request.GET.get('min_rating'))
        except (TypeError, ValueError):
            pass
    if request.GET.get('category'):
        filters['category_id'] = request.GET.get('category')
    return render(request, 'browse_workers.html', {
        'workers': get_workers_list(filters),
        'categories': get_categories_list(),
        'selected_category': request.GET.get('category', ''),
    })


def worker_profile(request, worker_id):
    """Public worker profile — browse without booking login optional."""
    worker = get_object_or_404(Worker.objects.select_related('user'), pk=worker_id, is_available=True)
    w = worker_dict(worker)
    reviews = get_worker_public_reviews(worker)
    from users.availability import get_worker_availability

    availability = get_worker_availability(worker)
    can_book = request.user.is_authenticated and request.user.user_type == 'user'
    return render(request, 'worker_profile.html', {
        'worker': w,
        'reviews': reviews,
        'availability': availability,
        'can_book': can_book,
    })


def start_client(request):
    if request.user.is_authenticated and request.user.user_type == 'user':
        return redirect('browse_workers')
    return redirect('auth')


def start_worker(request):
    if request.user.is_authenticated and request.user.user_type == 'worker':
        return redirect('worker_dashboard')
    return redirect('/auth/?tab=worker')


def contact_submit(request):
    if request.method == 'POST':
        messages.success(request, 'Thank you! We will respond soon.')
        logger.info('Contact form submitted by %s', request.POST.get('email', 'anonymous'))
    return redirect('index')


def landing_pricing(request):
    return _render_landing(request, 'Pricing', 'Transparent fees and escrow protection.', 'landing/pricing_content.html')


def landing_faq(request):
    return _render_landing(request, 'FAQs', 'Common questions about ProTech.', 'landing/faq_content.html')


def landing_support(request):
    return _render_landing(request, 'Support', 'We are here to help.', 'landing/support_content.html')


def landing_privacy(request):
    return _render_landing(request, 'Privacy Policy', 'How we protect your data.', 'landing/privacy_content.html')


def landing_terms(request):
    return _render_landing(request, 'Terms of Service', 'Platform terms and conditions.', 'landing/terms_content.html')


def landing_careers(request):
    return _render_landing(request, 'Careers', 'Join the ProTech team.', 'landing/careers_content.html')


def landing_blog(request):
    return _render_landing(request, 'Blog', 'News and insights.', 'landing/blog_content.html')


def landing_success_stories(request):
    return _render_landing(request, 'Success Stories', 'Real results from our community.', 'landing/success_stories_content.html')


def landing_resources(request):
    return _render_landing(request, 'Resources', 'Guides for clients and professionals.', 'landing/resources_content.html')


@login_required
def notifications_page(request):
    if request.GET.get('mark_all'):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return redirect('notifications_page')
    if request.GET.get('read'):
        Notification.objects.filter(user=request.user, id=request.GET.get('read')).update(is_read=True)
        return redirect('notifications_page')
    notes = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
    return render(request, 'notifications.html', {'notifications': notes})


@login_required
def messages_page(request):
    user = request.user
    booking_id = request.GET.get('booking') or request.POST.get('booking_id')
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        body = request.POST.get('message', '').strip()
        bid = request.POST.get('booking_id')
        if receiver_id and body:
            from django.contrib.auth import get_user_model

            receiver = get_object_or_404(get_user_model(), pk=receiver_id)
            booking = None
            if bid:
                booking = Booking.objects.filter(pk=bid).first()
            Message.objects.create(
                sender=user,
                receiver=receiver,
                message=body,
                booking=booking,
            )
            Notification.objects.create(
                user=receiver,
                title='New message',
                message=f'{display_name(user)} sent you a message.',
                type='message',
                link=f'/messages/?with={user.id}' + (f'&booking={bid}' if bid else ''),
            )
            from protech_project.email_notify import notify_user_email

            notify_user_email(
                receiver,
                'New message on ProTech',
                f'{display_name(user)} wrote: {body[:200]}',
            )
            messages.success(request, 'Message sent')
        redirect_url = f'/messages/?with={receiver_id}'
        if bid:
            redirect_url += f'&booking={bid}'
        return redirect(redirect_url)

    contacts = _message_contacts(user)
    other_id = request.GET.get('with')
    active_contact = None
    conversation = []
    if other_id:
        from django.contrib.auth import get_user_model

        other = get_object_or_404(get_user_model(), pk=other_id)
        active_contact = user_contact(other)
        conversation = Message.objects.filter(
            Q(sender=user, receiver=other) | Q(sender=other, receiver=user)
        ).select_related('sender', 'receiver').order_by('created_at')
        Message.objects.filter(sender=other, receiver=user, is_read=False).update(is_read=True)
    return render(request, 'messages.html', {
        'contacts': contacts,
        'conversation': conversation,
        'active_contact': active_contact,
        'other_id': int(other_id) if other_id else None,
        'booking_id': int(booking_id) if booking_id else None,
        'session': {'user_id': user.id},
    })


def _message_contacts(user):
    """Users the current user has bookings with or prior messages."""
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
    contacts = []
    for u in User.objects.filter(pk__in=ids):
        contacts.append(user_contact(u))
    contacts.sort(key=lambda c: c.name.lower())
    return contacts


@login_required
def reviews_page(request):
    pending = Booking.objects.filter(user=request.user, status='completed').exclude(
        id__in=Review.objects.filter(user=request.user).values_list('booking_id', flat=True)
    )
    given = Review.objects.filter(user=request.user).select_related('worker__user', 'booking')
    return render(request, 'reviews_list.html', {'pending': pending, 'reviews': given})


@login_required
@user_type_required('user')
def favorites_page(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        worker_id = request.POST.get('worker_id')
        worker = get_object_or_404(Worker, pk=worker_id)
        if action == 'add':
            Favorite.objects.get_or_create(user=request.user, worker=worker)
            messages.success(request, 'Saved to favorites')
        elif action == 'remove':
            Favorite.objects.filter(user=request.user, worker=worker).delete()
        return redirect(request.META.get('HTTP_REFERER', 'browse_workers'))
    favorites = Favorite.objects.filter(user=request.user).select_related('worker__user')
    workers = [worker_dict(f.worker) for f in favorites]
    return render(request, 'favorites.html', {'workers': workers})


@login_required
def profile_page(request):
    worker = None
    if request.user.user_type == 'worker':
        worker = Worker.objects.filter(user=request.user).first()
    return render(request, 'profile.html', {
        'profile_user': request.user,
        'worker': worker_dict(worker) if worker else None,
    })


@login_required
def settings_page(request):
    worker = None
    availability_rows = []
    if request.user.user_type == 'worker':
        worker = Worker.objects.filter(user=request.user).first()
        if worker:
            availability_rows = get_worker_availability(worker)
    if request.method == 'POST':
        form_type = request.POST.get('form_type', 'profile')
        if form_type == 'password':
            current = request.POST.get('current_password', '')
            new_pw = request.POST.get('new_password', '')
            confirm = request.POST.get('confirm_password', '')
            if not request.user.check_password(current):
                messages.error(request, 'Current password is incorrect')
            elif new_pw != confirm or len(new_pw) < 6:
                messages.error(request, 'New passwords must match and be at least 6 characters')
            else:
                request.user.set_password(new_pw)
                request.user.save()
                messages.success(request, 'Password updated — please log in again')
                return redirect('auth')
        else:
            request.user.first_name = request.POST.get('name', request.user.first_name)
            request.user.phone = request.POST.get('phone', request.user.phone)
            request.user.save(update_fields=['first_name', 'phone'])
            if worker:
                worker.service_area = request.POST.get('service_area', worker.service_area)
                worker.skills = request.POST.get('skills', worker.skills)
                worker.bio = request.POST.get('bio', worker.bio or '')
                try:
                    worker.experience = int(request.POST.get('experience') or worker.experience)
                except (TypeError, ValueError):
                    pass
                worker.save()
                save_worker_availability(worker, request.POST)
                availability_rows = get_worker_availability(worker)
            messages.success(request, 'Settings updated')
            return redirect('settings_page')
    user_ctx = user_contact(request.user)
    return render(request, 'settings.html', {
        'user': user_ctx,
        'user_type': request.user.user_type,
        'worker': worker,
        'availability_rows': availability_rows,
    })
