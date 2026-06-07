from datetime import date, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from bookings.models import Booking
from escrow.services import deposit_demo_funds, fund_escrow
from users.models import ServiceCategory, Worker, WorkerAvailability

User = get_user_model()


class BookingFeatureTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.client_user = User.objects.create_user(
            username='john@test.com',
            email='john@test.com',
            password='password123',
            phone='+10000000002',
            user_type='user',
        )
        worker_user = User.objects.create_user(
            username='mike@test.com',
            email='mike@test.com',
            password='password123',
            phone='+10000000003',
            user_type='worker',
        )
        self.worker = Worker.objects.create(
            user=worker_user,
            service_area='Test City',
            skills='Plumbing',
            experience=5,
            hourly_rate=50,
        )
        self.category = ServiceCategory.objects.create(name='Plumbing', description='Pipes')
        WorkerAvailability.objects.create(
            worker=self.worker,
            day_of_week=0,
            start_time='09:00',
            end_time='17:00',
        )
        deposit_demo_funds(self.client_user, 200)

    def _monday_on_or_after(self, start):
        d = start
        while d.weekday() != 0:
            d += timedelta(days=1)
        return d

    def test_booking_saves_service_category(self):
        self.client.login(username='john@test.com', password='password123')
        sched = self._monday_on_or_after(date.today() + timedelta(days=1))
        response = self.client.post(
            reverse('book_worker', kwargs={'worker_id': self.worker.id}),
            {
                'title': 'Pipe fix',
                'description': 'Leaking pipe',
                'service_category_id': self.category.id,
                'scheduled_date': sched.isoformat(),
                'scheduled_time': '10:00',
                'address': '123 Main',
                'price': '80',
                'estimated_duration': '60',
            },
        )
        self.assertEqual(response.status_code, 302)
        booking = Booking.objects.latest('id')
        self.assertEqual(booking.service_category_id, self.category.id)

    def test_start_requires_escrow(self):
        sched = self._monday_on_or_after(date.today() + timedelta(days=1))
        booking = Booking.objects.create(
            user=self.client_user,
            worker=self.worker,
            title='Test job',
            description='Fix sink',
            scheduled_date=sched,
            scheduled_time=time(10, 0),
            address='123 Main',
            price=Decimal('80.00'),
            status='confirmed',
        )
        self.client.login(username='mike@test.com', password='password123')
        self.client.post(
            reverse('update_booking', kwargs={'booking_id': booking.id}),
            {'action': 'start'},
        )
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'confirmed')

    def test_start_after_escrow(self):
        sched = self._monday_on_or_after(date.today() + timedelta(days=1))
        booking = Booking.objects.create(
            user=self.client_user,
            worker=self.worker,
            title='Test job',
            description='Fix sink',
            scheduled_date=sched,
            scheduled_time=time(10, 0),
            address='123 Main',
            price=Decimal('80.00'),
            status='confirmed',
        )
        fund_escrow(booking, self.client_user)
        self.client.login(username='mike@test.com', password='password123')
        self.client.post(
            reverse('update_booking', kwargs={'booking_id': booking.id}),
            {'action': 'start'},
        )
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'in_progress')

    def test_worker_profile_public(self):
        response = self.client.get(reverse('worker_profile', kwargs={'worker_id': self.worker.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Plumbing')

    def test_booking_detail_page(self):
        sched = self._monday_on_or_after(date.today() + timedelta(days=1))
        booking = Booking.objects.create(
            user=self.client_user,
            worker=self.worker,
            title='Detail test',
            scheduled_date=sched,
            scheduled_time=time(10, 0),
            address='123 Main',
            price=Decimal('50.00'),
        )
        self.client.login(username='john@test.com', password='password123')
        response = self.client.get(reverse('booking_detail', kwargs={'booking_id': booking.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Detail test')
