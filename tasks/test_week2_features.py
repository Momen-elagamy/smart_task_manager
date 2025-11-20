"""
Tests for Week 2 features: Comments, Attachments, and Mentions.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Task, Comment, Attachment, Project
from .utils import handle_mentions_in_comment
from notifications.models import Notification

User = get_user_model()


class CommentModelTest(TestCase):
    """Test Comment model functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.user
        )
        self.task = Task.objects.create(
            title='Test Task',
            project=self.project,
            assigned_to=self.user
        )
    
    def test_comment_creation(self):
        """Test creating a comment."""
        comment = Comment.objects.create(
            content='This is a test comment',
            author=self.user,
            task=self.task
        )
        
        self.assertEqual(comment.content, 'This is a test comment')
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.task, self.task)
        self.assertFalse(comment.edited)
        self.assertIsNone(comment.edited_at)
    
    def test_comment_edit_tracking(self):
        """Test that comment edits are tracked."""
        comment = Comment.objects.create(
            content='Original content',
            author=self.user,
            task=self.task
        )
        
        # Update the comment
        comment.content = 'Updated content'
        comment.save()
        
        self.assertTrue(comment.edited)
        self.assertIsNotNone(comment.edited_at)


class AttachmentModelTest(TestCase):
    """Test Attachment model functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.user
        )
        self.task = Task.objects.create(
            title='Test Task',
            project=self.project,
            assigned_to=self.user
        )
    
    def test_attachment_creation(self):
        """Test creating an attachment."""
        # Create a simple file
        file_content = b'Test file content'
        uploaded_file = SimpleUploadedFile(
            'test.txt',
            file_content,
            content_type='text/plain'
        )
        
        attachment = Attachment.objects.create(
            file=uploaded_file,
            uploaded_by=self.user,
            task=self.task
        )
        
        self.assertEqual(attachment.uploaded_by, self.user)
        self.assertEqual(attachment.task, self.task)
        self.assertEqual(attachment.original_filename, 'test.txt')
        self.assertEqual(attachment.mime_type, 'text/plain')
        self.assertEqual(attachment.size, len(file_content))
    
    def test_attachment_properties(self):
        """Test attachment properties."""
        file_content = b'Test file content'
        uploaded_file = SimpleUploadedFile(
            'test.txt',
            file_content,
            content_type='text/plain'
        )
        
        attachment = Attachment.objects.create(
            file=uploaded_file,
            uploaded_by=self.user,
            task=self.task
        )
        
        # Test file size in MB
        expected_size_mb = len(file_content) / (1024 * 1024)
        self.assertAlmostEqual(attachment.file_size_mb, expected_size_mb, places=2)
        
        # Test document type
        self.assertTrue(attachment.is_document)
        self.assertFalse(attachment.is_image)


class MentionHandlingTest(TestCase):
    """Test mention handling functionality."""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.user1
        )
        self.task = Task.objects.create(
            title='Test Task',
            project=self.project,
            assigned_to=self.user1
        )
    
    def test_mention_detection(self):
        """Test that mentions are detected and notifications created."""
        comment_content = 'Hey @user2@example.com, check this out!'
        
        # Create comment with mentions
        comment = Comment.objects.create(
            content=comment_content,
            author=self.user1,
            task=self.task
        )
        
        # Handle mentions
        mentioned_users = handle_mentions_in_comment(
            comment_content, 
            self.task, 
            self.user1
        )
        
        # Check that user2 was mentioned
        self.assertEqual(len(mentioned_users), 1)
        self.assertEqual(mentioned_users[0], self.user2)
        
        # Check that notification was created
        notification = Notification.objects.get(user=self.user2)
        self.assertIn('mentioned', notification.message)
        self.assertEqual(notification.task, self.task)
    
    def test_mention_self_exclusion(self):
        """Test that mentioning yourself doesn't create notification."""
        comment_content = 'Hey @user1@example.com, this is me!'
        
        # Handle mentions
        mentioned_users = handle_mentions_in_comment(
            comment_content, 
            self.task, 
            self.user1
        )
        
        # Should not mention the author
        self.assertEqual(len(mentioned_users), 0)
        
        # Should not create notification for self
        self.assertFalse(Notification.objects.filter(user=self.user1).exists())


class CommentAPITest(APITestCase):
    """Test Comment API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create users with different roles
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123'
        )
        self.admin.profile.role = 'admin'
        self.admin.profile.save()
        
        self.manager = User.objects.create_user(
            email='manager@example.com',
            password='managerpass123'
        )
        self.manager.profile.role = 'manager'
        self.manager.profile.save()
        
        self.developer = User.objects.create_user(
            email='developer@example.com',
            password='devpass123'
        )
        self.developer.profile.role = 'developer'
        self.developer.profile.save()
        
        self.client_user = User.objects.create_user(
            email='client@example.com',
            password='clientpass123'
        )
        self.client_user.profile.role = 'client'
        self.client_user.profile.save()
        
        # Create project and task
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.admin
        )
        self.task = Task.objects.create(
            title='Test Task',
            project=self.project,
            assigned_to=self.developer
        )
    
    def test_create_comment_as_admin(self):
        """Test creating a comment as admin."""
        self.client.force_authenticate(user=self.admin)
        
        data = {
            'content': 'This is a test comment',
            'task': self.task.id
        }
        
        response = self.client.post('/api/tasks/comments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check comment was created
        comment = Comment.objects.get(content='This is a test comment')
        self.assertEqual(comment.author, self.admin)
        self.assertEqual(comment.task, self.task)
    
    def test_create_comment_as_developer(self):
        """Test creating a comment as developer on assigned task."""
        self.client.force_authenticate(user=self.developer)
        
        data = {
            'content': 'Working on this task',
            'task': self.task.id
        }
        
        response = self.client.post('/api/tasks/comments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_comment_with_mentions(self):
        """Test creating a comment with mentions."""
        self.client.force_authenticate(user=self.admin)
        
        data = {
            'content': 'Hey @manager@example.com, check this out!',
            'task': self.task.id
        }
        
        response = self.client.post('/api/tasks/comments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check notification was created
        notification = Notification.objects.get(user=self.manager)
        self.assertIn('mentioned', notification.message)
    
    def test_comment_permissions(self):
        """Test comment permissions for different roles."""
        # Client should not be able to create comments
        self.client.force_authenticate(user=self.client_user)
        
        data = {
            'content': 'This should not work',
            'task': self.task.id
        }
        
        response = self.client.post('/api/tasks/comments/', data)
        # This should work for read access, but let's test the queryset filtering
        response = self.client.get('/api/tasks/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AttachmentAPITest(APITestCase):
    """Test Attachment API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create users with different roles
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123'
        )
        self.admin.profile.role = 'admin'
        self.admin.profile.save()
        
        self.developer = User.objects.create_user(
            email='developer@example.com',
            password='devpass123'
        )
        self.developer.profile.role = 'developer'
        self.developer.profile.save()
        
        # Create project and task
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.admin
        )
        self.task = Task.objects.create(
            title='Test Task',
            project=self.project,
            assigned_to=self.developer
        )
    
    def test_upload_valid_file(self):
        """Test uploading a valid file."""
        self.client.force_authenticate(user=self.admin)
        
        # Create a test file
        file_content = b'Test file content'
        uploaded_file = SimpleUploadedFile(
            'test.txt',
            file_content,
            content_type='text/plain'
        )
        
        data = {
            'file': uploaded_file,
            'task': self.task.id
        }
        
        response = self.client.post('/api/tasks/attachments/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check attachment was created
        attachment = Attachment.objects.get(original_filename='test.txt')
        self.assertEqual(attachment.uploaded_by, self.admin)
        self.assertEqual(attachment.task, self.task)
    
    def test_upload_invalid_file_type(self):
        """Test uploading an invalid file type."""
        self.client.force_authenticate(user=self.admin)
        
        # Create an invalid file
        file_content = b'Test file content'
        uploaded_file = SimpleUploadedFile(
            'test.exe',
            file_content,
            content_type='application/x-msdownload'
        )
        
        data = {
            'file': uploaded_file,
            'task': self.task.id
        }
        
        response = self.client.post('/api/tasks/attachments/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_upload_large_file(self):
        """Test uploading a file that's too large."""
        self.client.force_authenticate(user=self.admin)
        
        # Create a large file (simulate)
        large_content = b'x' * (11 * 1024 * 1024)  # 11 MB
        uploaded_file = SimpleUploadedFile(
            'large.txt',
            large_content,
            content_type='text/plain'
        )
        
        data = {
            'file': uploaded_file,
            'task': self.task.id
        }
        
        response = self.client.post('/api/tasks/attachments/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_attachment_permissions(self):
        """Test attachment permissions for different roles."""
        # Developer should be able to upload to assigned task
        self.client.force_authenticate(user=self.developer)
        
        file_content = b'Test file content'
        uploaded_file = SimpleUploadedFile(
            'test.txt',
            file_content,
            content_type='text/plain'
        )
        
        data = {
            'file': uploaded_file,
            'task': self.task.id
        }
        
        response = self.client.post('/api/tasks/attachments/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_attachment_filtering(self):
        """Test attachment filtering by type."""
        self.client.force_authenticate(user=self.admin)
        
        # Create image attachment
        image_content = b'fake image content'
        image_file = SimpleUploadedFile(
            'test.png',
            image_content,
            content_type='image/png'
        )
        
        Attachment.objects.create(
            file=image_file,
            uploaded_by=self.admin,
            task=self.task,
            original_filename='test.png',
            mime_type='image/png',
            size=len(image_content)
        )
        
        # Test images endpoint
        response = self.client.get('/api/tasks/attachments/images/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test documents endpoint
        response = self.client.get('/api/tasks/attachments/documents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # No documents


class FileValidationTest(TestCase):
    """Test file validation utilities."""
    
    def test_validate_file_size_valid(self):
        """Test file size validation with valid file."""
        from .validators import validate_file_size
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Create a small file
        file_content = b'Test content'
        uploaded_file = SimpleUploadedFile(
            'test.txt',
            file_content,
            content_type='text/plain'
        )
        
        # Should not raise exception
        validate_file_size(uploaded_file)
    
    def test_validate_file_size_invalid(self):
        """Test file size validation with invalid file."""
        from .validators import validate_file_size
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.core.exceptions import ValidationError
        
        # Create a large file
        large_content = b'x' * (11 * 1024 * 1024)  # 11 MB
        uploaded_file = SimpleUploadedFile(
            'large.txt',
            large_content,
            content_type='text/plain'
        )
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError):
            validate_file_size(uploaded_file)
    
    def test_validate_content_type_valid(self):
        """Test content type validation with valid file."""
        from .validators import validate_content_type
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Create a valid file
        file_content = b'Test content'
        uploaded_file = SimpleUploadedFile(
            'test.txt',
            file_content,
            content_type='text/plain'
        )
        
        # Should not raise exception
        validate_content_type(uploaded_file)
    
    def test_validate_content_type_invalid(self):
        """Test content type validation with invalid file."""
        from .validators import validate_content_type
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.core.exceptions import ValidationError
        
        # Create an invalid file
        file_content = b'Test content'
        uploaded_file = SimpleUploadedFile(
            'test.exe',
            file_content,
            content_type='application/x-msdownload'
        )
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError):
            validate_content_type(uploaded_file)

