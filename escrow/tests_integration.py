from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from bookings.models import Booking
from escrow.services import deposit_demo_funds, ensure_wallet, fund_escrow
from users.models import Worker

User = get_user_model()


class EscrowServiceTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username='c@test.com', email='c@test.com', password='x', user_type='user'
        )
        worker_user = User.objects.create_user(
            username='w@test.com', email='w@test.com', password='x', user_type='worker'
        )
        self.worker = Worker.objects.create(
            user=worker_user, service_area='City', skills='Test', hourly_rate=100
        )
        deposit_demo_funds(self.client_user, 150)

    def test_fund_escrow_moves_balance(self):
        booking = Booking.objects.create(
            user=self.client_user,
            worker=self.worker,
            title='Test job',
            scheduled_date='2026-06-10',
            scheduled_time='10:00',
            address='123 St',
            price=Decimal('80.00'),
        )
        fund_escrow(booking, self.client_user)
        wallet = ensure_wallet(self.client_user)
        self.assertEqual(wallet.available_balance, Decimal('70.00'))
        self.assertEqual(booking.payment_status, 'escrow_held')
