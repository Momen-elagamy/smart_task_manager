"""
Subtasks and Time Tracking Models
"""
from django.db import models
from django.contrib.auth import get_user_model
from tasks.models import Task
from django.core.validators import MinValueValidator

User = get_user_model()


class Subtask(models.Model):
    """Subtasks for breaking down main tasks"""
    parent_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='subtasks_assigned')
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
        ],
        default='pending'
    )
    order = models.IntegerField(default=0)
    estimated_minutes = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    actual_minutes = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['parent_task', 'status']),
        ]
    
    def __str__(self):
        return f"{self.parent_task.title} > {self.title}"
    
    @property
    def completion_percentage(self):
        """Calculate completion based on time"""
        if self.status == 'completed':
            return 100
        if self.estimated_minutes and self.actual_minutes:
            return min(100, int((self.actual_minutes / self.estimated_minutes) * 100))
        return 0


class TimeEntry(models.Model):
    """Time tracking entries for tasks"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_entries')
    subtask = models.ForeignKey(Subtask, on_delete=models.CASCADE, null=True, blank=True, related_name='time_entries')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_entries')
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    is_billable = models.BooleanField(default=False)
    is_running = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_time']
        verbose_name = 'Time Entry'
        verbose_name_plural = 'Time Entries'
        indexes = [
            models.Index(fields=['task', 'user', 'start_time']),
            models.Index(fields=['is_running']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.task.title} ({self.duration_minutes}m)"
    
    def save(self, *args, **kwargs):
        """Calculate duration if end_time is set"""
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            self.duration_minutes = int(delta.total_seconds() / 60)
            self.is_running = False
        super().save(*args, **kwargs)
    
    def stop(self):
        """Stop the timer"""
        from django.utils import timezone
        if self.is_running:
            self.end_time = timezone.now()
            self.save()


class TaskTemplate(models.Model):
    """Reusable task templates"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_templates')
    category = models.CharField(max_length=100, blank=True)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    default_priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('urgent', 'Urgent'),
        ],
        default='medium'
    )
    checklist_items = models.JSONField(default=list)  # List of subtask titles
    tags = models.JSONField(default=list)
    is_public = models.BooleanField(default=False)
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return self.name
    
    def create_task_from_template(self, project, assigned_to=None, due_date=None):
        """Create a task from this template"""
        task = Task.objects.create(
            title=self.name,
            description=self.description,
            project=project,
            assigned_to=assigned_to or self.created_by,
            priority=self.default_priority,
            due_date=due_date,
            estimated_hours=self.estimated_hours or 0
        )
        
        # Create subtasks from checklist
        for i, item in enumerate(self.checklist_items):
            Subtask.objects.create(
                parent_task=task,
                title=item,
                order=i
            )
        
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
        
        return task
