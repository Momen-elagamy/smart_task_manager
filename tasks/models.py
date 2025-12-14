import uuid
from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from projects.models import Project
from django.utils import timezone


def validate_file_size(value):
    """Validate file size is under 10MB"""
    limit = 10 * 1024 * 1024  # 10MB
    if value.size > limit:
        raise ValidationError('File size cannot exceed 10MB.')


def validate_file_extension_secure(value):
    """Extra validation to block potentially dangerous file types"""
    dangerous_extensions = ['exe', 'bat', 'cmd', 'sh', 'ps1', 'msi', 'com', 'scr', 'vbs']
    ext = value.name.split('.')[-1].lower() if '.' in value.name else ''
    if ext in dangerous_extensions:
        raise ValidationError(f'File type .{ext} is not allowed for security reasons.')


class Task(models.Model):
    STATUS_CHOICES = (
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    )
    RECURRENCE_CHOICES = (
        ('none', 'None'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    due_date = models.DateField(blank=True, null=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assigned_tasks', on_delete=models.SET_NULL, blank=True, null=True)
    depends_on = models.ForeignKey('self', related_name='dependents', on_delete=models.SET_NULL, blank=True, null=True)
    recurrence = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, default='none')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        indexes = [
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['project', 'status']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.title

    @property
    def comments_count(self):
        return self.comments.count()

    @property
    def attachments_count(self):
        return self.attachments.count()


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='task_comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return f"Comment by {self.author} on {self.task}"

    def mark_edited(self):
        self.edited = True
        self.edited_at = timezone.now()
        self.save(update_fields=['edited', 'edited_at'])


class Attachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(
        upload_to='task_attachments/',
        validators=[
            FileExtensionValidator(allowed_extensions=['png','jpg','jpeg','pdf','txt','docx','doc','zip','xlsx','xls']),
            validate_file_size,
            validate_file_extension_secure
        ]
    )
    original_filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100)
    size = models.PositiveIntegerField()
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='task_attachments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Attachment'
        verbose_name_plural = 'Attachments'

    def __str__(self):
        return f"Attachment for {self.task}"

    @property
    def file_size_mb(self):
        return round(self.size / (1024 * 1024), 2) if self.size else 0

    @property
    def is_image(self):
        return self.mime_type.startswith('image/') if self.mime_type else False

    @property
    def is_document(self):
        doc_types = ['application/pdf','text/plain','application/msword',
                     'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                     'application/vnd.ms-excel','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
        return self.mime_type in doc_types if self.mime_type else False


class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=20, default='#06b6d4')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_tags', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tasks = models.ManyToManyField(Task, related_name='tags', blank=True)

    def __str__(self):
        return self.name
