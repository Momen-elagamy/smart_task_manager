"""
Smart Notifications and Reminders System
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class NotificationPreference(models.Model):
    """User notification preferences"""
    
    CHANNEL_CHOICES = [
        ('web', 'Web Push'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('slack', 'Slack'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Global settings
    enabled = models.BooleanField(default=True)
    do_not_disturb = models.BooleanField(default=False)
    dnd_start_time = models.TimeField(null=True, blank=True, help_text='Do not disturb start time')
    dnd_end_time = models.TimeField(null=True, blank=True, help_text='Do not disturb end time')
    
    # Channel preferences
    channels = models.JSONField(default=list)  # ['web', 'email']
    
    # Event preferences
    task_assigned = models.BooleanField(default=True)
    task_due_soon = models.BooleanField(default=True)
    task_overdue = models.BooleanField(default=True)
    task_completed = models.BooleanField(default=True)
    task_commented = models.BooleanField(default=True)
    task_mentioned = models.BooleanField(default=True)
    
    project_added = models.BooleanField(default=True)
    project_updated = models.BooleanField(default=False)
    
    chat_message = models.BooleanField(default=True)
    chat_mentioned = models.BooleanField(default=True)
    
    # Digest settings
    daily_digest = models.BooleanField(default=False)
    weekly_digest = models.BooleanField(default=True)
    digest_time = models.TimeField(default='09:00:00')
    digest_day = models.IntegerField(default=1, help_text='Day of week for weekly digest (0=Monday)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification Preference'
    
    def __str__(self):
        return f"Preferences for {self.user.email}"
    
    def is_dnd_active(self):
        """Check if Do Not Disturb is currently active"""
        if not self.do_not_disturb or not self.dnd_start_time or not self.dnd_end_time:
            return False
        
        now = timezone.localtime(timezone.now()).time()
        
        if self.dnd_start_time < self.dnd_end_time:
            return self.dnd_start_time <= now <= self.dnd_end_time
        else:  # Spans midnight
            return now >= self.dnd_start_time or now <= self.dnd_end_time
    
    def should_notify(self, event_type, channel='web'):
        """Check if user should be notified for event"""
        if not self.enabled:
            return False
        
        if self.is_dnd_active():
            return False
        
        if channel not in self.channels:
            return False
        
        # Check event-specific preference
        return getattr(self, event_type, True)


class SmartReminder(models.Model):
    """Smart reminders for tasks"""
    
    REMINDER_TYPE_CHOICES = [
        ('before_due', 'Before Due Date'),
        ('at_due', 'At Due Date'),
        ('after_overdue', 'After Overdue'),
        ('daily', 'Daily'),
        ('custom', 'Custom'),
    ]
    
    task = models.ForeignKey('tasks.Task', on_delete=models.CASCADE, related_name='reminders')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES)
    
    # Timing
    remind_at = models.DateTimeField()
    minutes_before = models.IntegerField(null=True, blank=True, help_text='Minutes before due date')
    
    # Status
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    is_snoozed = models.BooleanField(default=False)
    snooze_until = models.DateTimeField(null=True, blank=True)
    
    # Recurrence
    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.JSONField(null=True, blank=True)  # iCal RRULE format
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['remind_at']
        indexes = [
            models.Index(fields=['remind_at', 'is_sent']),
            models.Index(fields=['user', 'is_sent']),
        ]
    
    def __str__(self):
        return f"Reminder for {self.task.title} at {self.remind_at}"
    
    def snooze(self, minutes=30):
        """Snooze reminder for X minutes"""
        self.is_snoozed = True
        self.snooze_until = timezone.now() + timedelta(minutes=minutes)
        self.save()
    
    def is_due(self):
        """Check if reminder is due"""
        if self.is_sent and not self.is_recurring:
            return False
        
        if self.is_snoozed and self.snooze_until > timezone.now():
            return False
        
        return timezone.now() >= self.remind_at
    
    @classmethod
    def create_smart_reminders(cls, task):
        """Automatically create smart reminders for a task"""
        if not task.due_date or not task.assigned_to:
            return []
        
        reminders = []
        
        # 1 day before
        if task.due_date > timezone.now() + timedelta(days=1):
            reminders.append(cls.objects.create(
                task=task,
                user=task.assigned_to,
                reminder_type='before_due',
                remind_at=task.due_date - timedelta(days=1),
                minutes_before=1440
            ))
        
        # 1 hour before
        if task.due_date > timezone.now() + timedelta(hours=1):
            reminders.append(cls.objects.create(
                task=task,
                user=task.assigned_to,
                reminder_type='before_due',
                remind_at=task.due_date - timedelta(hours=1),
                minutes_before=60
            ))
        
        # At due date
        if task.due_date > timezone.now():
            reminders.append(cls.objects.create(
                task=task,
                user=task.assigned_to,
                reminder_type='at_due',
                remind_at=task.due_date
            ))
        
        return reminders


class DigestEmail(models.Model):
    """Email digests for users"""
    
    DIGEST_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='digests')
    digest_type = models.CharField(max_length=20, choices=DIGEST_TYPE_CHOICES)
    
    # Content
    tasks_created = models.IntegerField(default=0)
    tasks_completed = models.IntegerField(default=0)
    tasks_overdue = models.IntegerField(default=0)
    comments_received = models.IntegerField(default=0)
    mentions_count = models.IntegerField(default=0)
    
    # Detailed data
    summary_data = models.JSONField(default=dict)
    
    # Status
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-period_start']
        indexes = [
            models.Index(fields=['user', 'digest_type', 'period_start']),
        ]
    
    def __str__(self):
        return f"{self.digest_type} digest for {self.user.email}"
    
    def generate_summary(self):
        """Generate digest summary data"""
        from tasks.models import Task, Comment
        
        # Tasks created
        self.tasks_created = Task.objects.filter(
            assigned_to=self.user,
            created_at__gte=self.period_start,
            created_at__lte=self.period_end
        ).count()
        
        # Tasks completed
        self.tasks_completed = Task.objects.filter(
            assigned_to=self.user,
            status='completed',
            updated_at__gte=self.period_start,
            updated_at__lte=self.period_end
        ).count()
        
        # Tasks overdue
        self.tasks_overdue = Task.objects.filter(
            assigned_to=self.user,
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count()
        
        # Comments received
        user_tasks = Task.objects.filter(assigned_to=self.user)
        self.comments_received = Comment.objects.filter(
            task__in=user_tasks,
            created_at__gte=self.period_start,
            created_at__lte=self.period_end
        ).exclude(author=self.user).count()
        
        # Additional metrics
        self.summary_data = {
            'top_projects': list(Task.objects.filter(
                assigned_to=self.user
            ).values('project__name').annotate(
                count=models.Count('id')
            ).order_by('-count')[:5]),
            
            'completion_rate': self._calculate_completion_rate(),
            'avg_completion_time': self._calculate_avg_completion_time(),
        }
        
        self.save()
    
    def _calculate_completion_rate(self):
        """Calculate task completion rate"""
        from tasks.models import Task
        
        total = Task.objects.filter(
            assigned_to=self.user,
            created_at__gte=self.period_start,
            created_at__lte=self.period_end
        ).count()
        
        if total == 0:
            return 0
        
        completed = self.tasks_completed
        return round((completed / total) * 100, 1)
    
    def _calculate_avg_completion_time(self):
        """Calculate average time to complete tasks"""
        from tasks.models import Task
        from django.db.models import Avg, F
        
        avg = Task.objects.filter(
            assigned_to=self.user,
            status='completed',
            updated_at__gte=self.period_start,
            updated_at__lte=self.period_end
        ).aggregate(
            avg_time=Avg(F('updated_at') - F('created_at'))
        )['avg_time']
        
        if avg:
            return round(avg.total_seconds() / 3600, 1)  # Hours
        return 0


class NotificationQueue(models.Model):
    """Queue for sending notifications"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    message = models.TextField()
    data = models.JSONField(default=dict)
    channel = models.CharField(max_length=20, default='web')
    priority = models.IntegerField(default=5, help_text='1=highest, 10=lowest')
    
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    failed = models.BooleanField(default=False)
    failure_reason = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['priority', 'scheduled_for']
        indexes = [
            models.Index(fields=['is_sent', 'scheduled_for']),
            models.Index(fields=['user', 'is_sent']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} for {self.user.email}"
