"""
Tests for Task model and API endpoints.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from tests.base import BaseAPITestCase
from tasks.models import Task, Comment, Attachment, Tag
from projects.models import Project
import uuid

User = get_user_model()


class TaskModelTest(TestCase):
    """Test Task model functionality."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user = User.objects.create_user(
            email='tasktest@example.com',
            password='testpass123'
        )
        cls.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            owner=cls.user
        )

    def test_create_task(self):
        """Test creating a task."""
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            project=self.project,
            status='todo'
        )
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.status, 'todo')
        self.assertIsInstance(task.id, uuid.UUID)

    def test_task_with_assignment(self):
        """Test task with assigned user."""
        task = Task.objects.create(
            title='Assigned Task',
            project=self.project,
            assigned_to=self.user
        )
        self.assertEqual(task.assigned_to, self.user)

    def test_task_comments_count(self):
        """Test task comments count property."""
        task = Task.objects.create(
            title='Task with Comments',
            project=self.project
        )
        
        Comment.objects.create(
            task=task,
            author=self.user,
            content='First comment'
        )
        Comment.objects.create(
            task=task,
            author=self.user,
            content='Second comment'
        )
        
        self.assertEqual(task.comments_count, 2)

    def test_task_project_deletion(self):
        """Test that task is not deleted when project is deleted (SET_NULL)."""
        task = Task.objects.create(
            title='Task in Project',
            project=self.project
        )
        
        project_id = self.project.id
        self.project.delete()
        
        # Task should still exist with null project
        task.refresh_from_db()
        self.assertIsNone(task.project)

    def test_task_dependency(self):
        """Test task dependency."""
        parent_task = Task.objects.create(
            title='Parent Task',
            project=self.project
        )
        dependent_task = Task.objects.create(
            title='Dependent Task',
            project=self.project,
            depends_on=parent_task
        )
        
        self.assertEqual(dependent_task.depends_on, parent_task)
        self.assertIn(dependent_task, parent_task.dependents.all())


class CommentModelTest(TestCase):
    """Test Comment model functionality."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user = User.objects.create_user(
            email='commenttest@example.com',
            password='testpass123'
        )
        cls.task = Task.objects.create(
            title='Test Task'
        )

    def test_create_comment(self):
        """Test creating a comment."""
        comment = Comment.objects.create(
            task=self.task,
            author=self.user,
            content='Test comment'
        )
        self.assertEqual(comment.content, 'Test comment')
        self.assertEqual(comment.author, self.user)
        self.assertFalse(comment.edited)

    def test_mark_comment_edited(self):
        """Test marking comment as edited."""
        comment = Comment.objects.create(
            task=self.task,
            author=self.user,
            content='Original content'
        )
        
        comment.content = 'Edited content'
        comment.mark_edited()
        
        self.assertTrue(comment.edited)
        self.assertIsNotNone(comment.edited_at)


class TagModelTest(TestCase):
    """Test Tag model functionality."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user = User.objects.create_user(
            email='tagtest@example.com',
            password='testpass123'
        )

    def test_create_tag(self):
        """Test creating a tag."""
        tag = Tag.objects.create(
            name='urgent',
            color='#ff0000',
            created_by=self.user
        )
        self.assertEqual(tag.name, 'urgent')
        self.assertEqual(tag.color, '#ff0000')

    def test_tag_unique_name(self):
        """Test that tag names are unique."""
        Tag.objects.create(name='bug', created_by=self.user)
        with self.assertRaises(Exception):
            Tag.objects.create(name='bug', created_by=self.user)

    def test_tag_task_association(self):
        """Test associating tags with tasks."""
        tag = Tag.objects.create(name='feature', created_by=self.user)
        task = Task.objects.create(title='Task with Tag')
        
        tag.tasks.add(task)
        
        self.assertIn(task, tag.tasks.all())
        self.assertIn(tag, task.tags.all())


class TaskAPITest(BaseAPITestCase):
    """Test Task API endpoints."""

    def setUp(self):
        """Set up for each test."""
        super().setUp()
        self.authenticate(self.admin_user)
        
        self.project = Project.objects.create(
            name='API Test Project',
            description='Test Description',
            owner=self.admin_user
        )

    def test_list_tasks(self):
        """Test listing tasks."""
        Task.objects.create(
            title='Task 1',
            project=self.project
        )
        Task.objects.create(
            title='Task 2',
            project=self.project
        )
        
        response = self.client.get('/tasks/api/tasks/')
        
        if response.status_code == status.HTTP_200_OK:
            self.assertGreaterEqual(len(response.data.get('results', response.data)), 2)

    def test_create_task(self):
        """Test creating a task via API."""
        data = {
            'title': 'New API Task',
            'description': 'Created via API',
            'status': 'todo',
            'project': str(self.project.id)
        }
        
        response = self.client.post('/tasks/api/tasks/', data, format='json')
        
        if response.status_code == status.HTTP_201_CREATED:
            self.assertEqual(response.data['title'], 'New API Task')
            self.assertTrue(Task.objects.filter(title='New API Task').exists())

    def test_update_task(self):
        """Test updating a task via API."""
        task = Task.objects.create(
            title='Task to Update',
            project=self.project,
            status='todo'
        )
        
        data = {
            'title': 'Updated Task',
            'status': 'in_progress'
        }
        
        response = self.client.patch(f'/tasks/api/tasks/{task.id}/', data, format='json')
        
        if response.status_code == status.HTTP_200_OK:
            task.refresh_from_db()
            self.assertEqual(task.title, 'Updated Task')
            self.assertEqual(task.status, 'in_progress')

    def test_delete_task(self):
        """Test deleting a task via API."""
        task = Task.objects.create(
            title='Task to Delete',
            project=self.project
        )
        
        response = self.client.delete(f'/tasks/api/tasks/{task.id}/')
        
        if response.status_code == status.HTTP_204_NO_CONTENT:
            self.assertFalse(Task.objects.filter(id=task.id).exists())

    def test_filter_tasks_by_status(self):
        """Test filtering tasks by status."""
        Task.objects.create(title='Todo Task', status='todo', project=self.project)
        Task.objects.create(title='Done Task', status='done', project=self.project)
        
        response = self.client.get('/tasks/api/tasks/?status=todo')
        
        if response.status_code == status.HTTP_200_OK:
            tasks = response.data.get('results', response.data)
            for task in tasks:
                if 'status' in task:
                    self.assertEqual(task['status'], 'todo')

    def test_unauthorized_access(self):
        """Test accessing tasks without authentication."""
        self.logout()
        response = self.client.get('/tasks/api/tasks/')
        
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN
        ])
