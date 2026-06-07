from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from users.models import Worker

User = get_user_model()


class AuthIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='client@test.com',
            email='client@test.com',
            password='password123',
            phone='+10000000001',
            user_type='user',
        )

    def test_health_endpoint(self):
        response = self.client.get(reverse('health'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')

    def test_login_and_dashboard_redirect(self):
        response = self.client.post(reverse('auth'), {
            'login': '1',
            'email': 'client@test.com',
            'password': 'password123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/user/dashboard', response.url)

    def test_client_cannot_access_worker_dashboard(self):
        self.client.login(username='client@test.com', password='password123')
        response = self.client.get(reverse('worker_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_password_reset_page_loads(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)


class BookingFlowTests(TestCase):
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

    def test_browse_workers_requires_login(self):
        response = self.client.get(reverse('browse_workers'))
        self.assertEqual(response.status_code, 302)

    def test_book_worker_page_after_login(self):
        self.client.login(username='john@test.com', password='password123')
        response = self.client.get(reverse('book_worker', kwargs={'worker_id': self.worker.id}))
        self.assertEqual(response.status_code, 200)
