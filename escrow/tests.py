from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import UserWallet, EscrowVault, EscrowHold, WalletTransaction

User = get_user_model()


class UserWalletModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            phone='+1234567890',
            user_type='user'
        )

    def test_create_wallet(self):
        wallet = UserWallet.objects.create(
            user=self.user,
            available_balance=100.00
        )
        self.assertEqual(wallet.user, self.user)
        self.assertEqual(wallet.available_balance, 100.00)


class EscrowVaultModelTest(TestCase):
    def test_create_escrow_vault(self):
        vault = EscrowVault.objects.create(
            id=1,
            total_held=500.00,
            total_released=1000.00
        )
        self.assertEqual(vault.id, 1)
        self.assertEqual(vault.total_held, 500.00)
        self.assertEqual(vault.total_released, 1000.00)


class WalletTransactionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            phone='+1234567890',
            user_type='user'
        )

    def test_create_transaction(self):
        transaction = WalletTransaction.objects.create(
            user=self.user,
            transaction_type='deposit',
            amount=100.00,
            balance_after=100.00,
            description='Initial deposit'
        )
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.transaction_type, 'deposit')
        self.assertEqual(transaction.amount, 100.00)
