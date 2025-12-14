"""
Base test configuration for Smart Task Manager.
"""
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class BaseTestCase(TestCase):
    """Base test case with common setup."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data once for all tests."""
        cls.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User'
        )
        cls.admin_user.profile.role = 'admin'
        cls.admin_user.profile.save()

        cls.manager_user = User.objects.create_user(
            email='manager@test.com',
            password='testpass123',
            first_name='Manager',
            last_name='User'
        )
        cls.manager_user.profile.role = 'manager'
        cls.manager_user.profile.save()

        cls.developer_user = User.objects.create_user(
            email='developer@test.com',
            password='testpass123',
            first_name='Developer',
            last_name='User'
        )
        cls.developer_user.profile.role = 'developer'
        cls.developer_user.profile.save()

        cls.client_user = User.objects.create_user(
            email='client@test.com',
            password='testpass123',
            first_name='Client',
            last_name='User'
        )
        # client_user already has default 'client' role

    def setUp(self):
        """Set up before each test."""
        self.client = APIClient()


class BaseAPITestCase(APITestCase):
    """Base API test case with authentication."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data once for all tests."""
        cls.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User'
        )
        cls.admin_user.profile.role = 'admin'
        cls.admin_user.profile.save()

        cls.manager_user = User.objects.create_user(
            email='manager@test.com',
            password='testpass123',
            first_name='Manager',
            last_name='User'
        )
        cls.manager_user.profile.role = 'manager'
        cls.manager_user.profile.save()

        cls.developer_user = User.objects.create_user(
            email='developer@test.com',
            password='testpass123',
            first_name='Developer',
            last_name='User'
        )
        cls.developer_user.profile.role = 'developer'
        cls.developer_user.profile.save()

    def setUp(self):
        """Set up before each test."""
        self.client = APIClient()

    def get_token_for_user(self, user):
        """Get JWT token for a user."""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def authenticate(self, user):
        """Authenticate client with user's token."""
        tokens = self.get_token_for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        return tokens

    def logout(self):
        """Clear authentication."""
        self.client.credentials()
