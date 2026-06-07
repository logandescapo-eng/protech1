from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, time
from .models import Review
from bookings.models import Booking
from users.models import Worker, ServiceCategory

User = get_user_model()


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='client',
            email='client@example.com',
            password='testpass123',
            phone='+1234567890',
            user_type='user'
        )
        self.worker_user = User.objects.create_user(
            username='worker',
            email='worker@example.com',
            password='testpass123',
            phone='+1234567891',
            user_type='worker'
        )
        self.worker = Worker.objects.create(
            user=self.worker_user,
            service_area='New York',
            skills='Plumbing',
            experience=5,
            hourly_rate=75.00
        )
        self.booking = Booking.objects.create(
            user=self.user,
            worker=self.worker,
            title='Fix leaky faucet',
            scheduled_date=date(2025, 12, 1),
            scheduled_time=time(10, 0),
            address='123 Main St',
            price=75.00,
            status='completed'
        )

    def test_create_review(self):
        review = Review.objects.create(
            booking=self.booking,
            user=self.user,
            worker=self.worker,
            rating=5,
            comment='Excellent service!'
        )
        self.assertEqual(review.booking, self.booking)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Excellent service!')
