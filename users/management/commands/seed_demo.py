from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from escrow.models import EscrowVault
from escrow.services import ensure_wallet, deposit_demo_funds
from users.models import ServiceCategory, Worker

User = get_user_model()

DEMO_CATEGORIES = [
    ('Plumbing', 'Pipe repair and installation', 'wrench'),
    ('Electrical', 'Wiring and electrical repairs', 'bolt'),
    ('Cleaning', 'Home and office cleaning', 'sparkles'),
    ('Carpentry', 'Woodwork and furniture', 'hammer'),
]


class Command(BaseCommand):
    help = 'Seed demo users, categories, and wallets for local development / defense demo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--if-empty',
            action='store_true',
            help='Only seed when no users exist (safe for container startup)',
        )

    def handle(self, *args, **options):
        if options['if_empty'] and User.objects.exists():
            self.stdout.write('Database already has users — skipping seed.')
            return

        for name, desc, icon in DEMO_CATEGORIES:
            ServiceCategory.objects.get_or_create(name=name, defaults={'description': desc, 'icon': icon})

        client, created = User.objects.update_or_create(
            email='john@example.com',
            defaults={
                'username': 'john@example.com',
                'first_name': 'John Client',
                'phone': '+15551234567',
                'user_type': 'user',
            },
        )
        client.set_password('password123')
        client.save()
        if created:
            self.stdout.write(self.style.SUCCESS('Created demo client john@example.com'))

        worker_user, w_created = User.objects.update_or_create(
            email='mike@example.com',
            defaults={
                'username': 'mike@example.com',
                'first_name': 'Mike Worker',
                'phone': '+15559876543',
                'user_type': 'worker',
            },
        )
        worker_user.set_password('password123')
        worker_user.save()
        Worker.objects.update_or_create(
            user=worker_user,
            defaults={
                'service_area': 'Yekaterinburg',
                'skills': 'Plumbing, Electrical',
                'experience': 8,
                'hourly_rate': 65,
                'rating': 4.8,
                'total_reviews': 12,
                'total_jobs': 45,
            },
        )
        if w_created:
            self.stdout.write(self.style.SUCCESS('Created demo worker mike@example.com'))

        admin_user, a_created = User.objects.update_or_create(
            email='admin@protech.com',
            defaults={
                'username': 'admin@protech.com',
                'first_name': 'Site',
                'last_name': 'Admin',
                'user_type': 'user',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        admin_user.set_password('password123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        if a_created:
            self.stdout.write(self.style.SUCCESS('Created Django admin admin@protech.com'))

        worker_obj = Worker.objects.get(user=worker_user)
        from users.models import WorkerAvailability
        for day in range(0, 5):
            WorkerAvailability.objects.update_or_create(
                worker=worker_obj,
                day_of_week=day,
                defaults={'start_time': '08:00', 'end_time': '18:00', 'is_available': True},
            )

        EscrowVault.objects.get_or_create(pk=1, defaults={'id': 1})
        for user in User.objects.all():
            ensure_wallet(user)
            if user.email == 'john@example.com':
                deposit_demo_funds(user, 200)

        self.stdout.write(self.style.SUCCESS(
            'Demo data ready.\n'
            '  App login: john@example.com / password123 (client)\n'
            '  App login: mike@example.com / password123 (worker)\n'
            '  Django admin: admin@protech.com / password123 at /admin/'
        ))
