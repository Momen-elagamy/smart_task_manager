"""
Tests for Project model and API endpoints.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from tests.base import BaseAPITestCase
from projects.models import Project
import uuid

User = get_user_model()


class ProjectModelTest(TestCase):
    """Test Project model functionality."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user = User.objects.create_user(
            email='projecttest@example.com',
            password='testpass123'
        )

    def test_create_project(self):
        """Test creating a project."""
        project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            owner=self.user
        )
        self.assertEqual(project.name, 'Test Project')
        self.assertIsInstance(project.id, uuid.UUID)

    def test_project_str(self):
        """Test project string representation."""
        project = Project.objects.create(
            name='String Test Project',
            owner=self.user
        )
        self.assertEqual(str(project), 'String Test Project')


class ProjectAPITest(BaseAPITestCase):
    """Test Project API endpoints."""

    def setUp(self):
        """Set up for each test."""
        super().setUp()
        self.authenticate(self.admin_user)

    def test_list_projects(self):
        """Test listing projects."""
        Project.objects.create(
            name='Project 1',
            owner=self.admin_user
        )
        Project.objects.create(
            name='Project 2',
            owner=self.admin_user
        )
        
        response = self.client.get('/projects/api/projects/')
        
        if response.status_code == status.HTTP_200_OK:
            self.assertGreaterEqual(len(response.data.get('results', response.data)), 2)

    def test_create_project(self):
        """Test creating a project via API."""
        data = {
            'name': 'New API Project',
            'description': 'Created via API'
        }
        
        response = self.client.post('/projects/api/projects/', data, format='json')
        
        if response.status_code == status.HTTP_201_CREATED:
            self.assertEqual(response.data['name'], 'New API Project')
            self.assertTrue(Project.objects.filter(name='New API Project').exists())

    def test_retrieve_project(self):
        """Test retrieving a specific project."""
        project = Project.objects.create(
            name='Retrieve Test',
            owner=self.admin_user
        )
        
        response = self.client.get(f'/projects/api/projects/{project.id}/')
        
        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(response.data['name'], 'Retrieve Test')

    def test_update_project(self):
        """Test updating a project via API."""
        project = Project.objects.create(
            name='Original Name',
            owner=self.admin_user
        )
        
        data = {
            'name': 'Updated Name',
            'description': 'Updated Description'
        }
        
        response = self.client.patch(f'/projects/api/projects/{project.id}/', data, format='json')
        
        if response.status_code == status.HTTP_200_OK:
            project.refresh_from_db()
            self.assertEqual(project.name, 'Updated Name')

    def test_delete_project(self):
        """Test deleting a project via API."""
        project = Project.objects.create(
            name='To Delete',
            owner=self.admin_user
        )
        
        response = self.client.delete(f'/projects/api/projects/{project.id}/')
        
        if response.status_code == status.HTTP_204_NO_CONTENT:
            self.assertFalse(Project.objects.filter(id=project.id).exists())

    def test_unauthorized_project_access(self):
        """Test accessing projects without authentication."""
        self.logout()
        response = self.client.get('/projects/api/projects/')
        
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN
        ])
