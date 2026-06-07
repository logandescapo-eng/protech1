from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, time
from .models import Booking
from users.models import Worker, ServiceCategory

User = get_user_model()


class BookingModelTest(TestCase):
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
        self.category = ServiceCategory.objects.create(
            name='Plumbing',
            description='Pipe repair',
            icon='wrench'
        )

    def test_create_booking(self):
        booking = Booking.objects.create(
            user=self.user,
            worker=self.worker,
            service_category=self.category,
            title='Fix leaky faucet',
            description='Kitchen faucet is leaking',
            scheduled_date=date(2025, 12, 1),
            scheduled_time=time(10, 0),
            address='123 Main St',
            price=75.00
        )
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.worker, self.worker)
        self.assertEqual(booking.status, 'pending')
        self.assertEqual(booking.payment_status, 'pending')
