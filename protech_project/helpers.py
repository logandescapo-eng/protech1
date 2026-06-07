"""Shared helpers for template-compatible dicts and display names."""

from types import SimpleNamespace


def display_name(user):
    full = user.get_full_name().strip()
    return full or user.username


def initials(name):
    parts = (name or 'U').split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return (name or 'U')[:2].upper()


def worker_dict(worker):
    user = worker.user
    name = display_name(user)
    return SimpleNamespace(
        id=worker.id,
        user_id=user.id,
        name=name,
        email=user.email,
        phone=user.phone,
        service_area=worker.service_area,
        skills=worker.skills,
        experience=worker.experience,
        hourly_rate=float(worker.hourly_rate),
        rating=float(worker.rating),
        total_reviews=worker.total_reviews,
        total_jobs=worker.total_jobs,
        is_available=worker.is_available,
        bio=worker.bio or '',
    )


def booking_dict(booking):
    worker = worker_dict(booking.worker)
    client_name = display_name(booking.user)
    escrow = None
    try:
        hold = booking.escrow_hold
        escrow = SimpleNamespace(
            amount=float(hold.amount),
            status=hold.status,
            platform_fee=float(hold.platform_fee),
        )
    except Exception:
        pass
    category_name = None
    if booking.service_category_id:
        category_name = booking.service_category.name
    return SimpleNamespace(
        id=booking.id,
        title=booking.title,
        description=booking.description,
        status=booking.status,
        payment_status=booking.payment_status,
        scheduled_date=booking.scheduled_date,
        scheduled_time=booking.scheduled_time,
        address=booking.address,
        price=float(booking.price),
        estimated_duration=booking.estimated_duration,
        worker_id=booking.worker_id,
        worker_name=worker.name,
        worker=worker,
        client_name=client_name,
        client_user_id=booking.user_id,
        category_name=category_name,
        escrow=escrow,
        created_at=getattr(booking, 'created_at', None),
    )


def user_contact(user):
    return SimpleNamespace(
        id=user.id,
        name=display_name(user),
        user_type=user.get_user_type_display() if hasattr(user, 'get_user_type_display') else user.user_type,
        email=user.email,
    )
