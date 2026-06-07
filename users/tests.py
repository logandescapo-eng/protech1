from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Worker, ServiceCategory, Message, Notification, Favorite

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            phone='+1234567890',
            user_type='user'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.user_type, 'user')
        self.assertTrue(user.check_password('testpass123'))

    def test_create_worker_user(self):
        user = User.objects.create_user(
            username='worker',
            email='worker@example.com',
            password='testpass123',
            phone='+1234567891',
            user_type='worker'
        )
        self.assertEqual(user.user_type, 'worker')


class WorkerModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='worker1',
            email='worker1@example.com',
            password='testpass123',
            phone='+1234567892',
            user_type='worker'
        )

    def test_create_worker(self):
        worker = Worker.objects.create(
            user=self.user,
            service_area='New York',
            skills='Plumbing, Electrical',
            experience=5,
            hourly_rate=75.00
        )
        self.assertEqual(worker.user, self.user)
        self.assertEqual(worker.service_area, 'New York')
        self.assertEqual(worker.hourly_rate, 75.00)


class ServiceCategoryModelTest(TestCase):
    def test_create_service_category(self):
        category = ServiceCategory.objects.create(
            name='Plumbing',
            description='Pipe repair and installation',
            icon='wrench'
        )
        self.assertEqual(category.name, 'Plumbing')
        self.assertEqual(category.icon, 'wrench')


class MessageModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123',
            phone='+1234567893',
            user_type='user'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123',
            phone='+1234567894',
            user_type='worker'
        )

    def test_create_message(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            message='Hello, I need your services'
        )
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.receiver, self.user2)
        self.assertFalse(message.is_read)
