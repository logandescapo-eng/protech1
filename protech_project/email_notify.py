"""Optional email notifications (console backend in dev, SMTP in production)."""

import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def notify_user_email(user, subject, body):
    """Send a plain-text email; failures are logged, not raised."""
    if not user or not getattr(user, 'email', None):
        return
    try:
        send_mail(
            subject=f'[ProTech] {subject}',
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info('Email sent to %s: %s', user.email, subject)
    except Exception as exc:
        logger.warning('Could not email %s (%s): %s', user.email, subject, exc)
