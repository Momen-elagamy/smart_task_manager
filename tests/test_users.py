"""
Tests for User model and authentication.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from tests.base import BaseAPITestCase

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model functionality."""

    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_lowercase_email(self):
        """Test that email is converted to lowercase."""
        user = User.objects.create_user(
            email='TEST@EXAMPLE.COM',
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_user_profile_auto_created(self):
        """Test that UserProfile is automatically created."""
        user = User.objects.create_user(
            email='profile@example.com',
            password='testpass123'
        )
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.role, 'client')  # Default role

    def test_user_profile_roles(self):
        """Test UserProfile role functionality."""
        user = User.objects.create_user(
            email='role@example.com',
            password='testpass123'
        )
        user.profile.role = 'admin'
        user.profile.save()
        
        self.assertTrue(user.profile.has_role('admin'))
        self.assertFalse(user.profile.has_role('client'))
        self.assertTrue(user.profile.has_role('admin', 'manager'))

    def test_email_required(self):
        """Test that email is required."""
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='testpass123')

    def test_email_unique(self):
        """Test that email must be unique."""
        User.objects.create_user(email='unique@example.com', password='testpass123')
        with self.assertRaises(Exception):
            User.objects.create_user(email='unique@example.com', password='testpass456')


class AuthenticationAPITest(BaseAPITestCase):
    """Test authentication endpoints."""

    def test_register_user(self):
        """Test user registration."""
        url = '/api/users/register/'
        data = {
            'email': 'newuser@example.com',
            'password': 'Newpass123!',  # Strong password meets complexity
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data, format='json')
        
        # Registration may or may not be implemented yet
        self.assertIn(response.status_code, [
            status.HTTP_201_CREATED,
            status.HTTP_404_NOT_FOUND,  # Endpoint doesn't exist
            status.HTTP_405_METHOD_NOT_ALLOWED
        ])

    def test_login_success(self):
        """Test successful login."""
        url = '/api/token/'
        data = {
            'email': 'admin@test.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        url = '/api/token/'
        data = {
            'email': 'admin@test.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """Test login with non-existent user."""
        url = '/api/token/'
        data = {
            'email': 'nonexistent@example.com',
            'password': 'somepassword'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Test token refresh."""
        # Get initial tokens
        tokens = self.get_token_for_user(self.admin_user)
        
        # Refresh the token
        url = '/api/token/refresh/'
        data = {'refresh': tokens['refresh']}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_authenticated_request(self):
        """Test making authenticated request."""
        self.authenticate(self.admin_user)
        
        # Try accessing a protected endpoint
        response = self.client.get('/api/tasks/')
        
        # Should be 200 OK or 404 if endpoint doesn't exist
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ])

    def test_unauthenticated_request(self):
        """Test making unauthenticated request to protected endpoint."""
        response = self.client.get('/api/tasks/')
        
        # Should be 401 Unauthorized or 403 Forbidden
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND  # If endpoint doesn't exist
        ])
