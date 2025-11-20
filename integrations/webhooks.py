"""
Webhook System for Integrations
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import requests
import hmac
import hashlib
import json

User = get_user_model()


class Webhook(models.Model):
    """Webhook configurations"""
    
    EVENT_CHOICES = [
        ('task.created', 'Task Created'),
        ('task.updated', 'Task Updated'),
        ('task.deleted', 'Task Deleted'),
        ('task.completed', 'Task Completed'),
        ('project.created', 'Project Created'),
        ('project.updated', 'Project Updated'),
        ('project.deleted', 'Project Deleted'),
        ('comment.created', 'Comment Created'),
        ('user.joined', 'User Joined Project'),
        ('*', 'All Events'),
    ]
    
    name = models.CharField(max_length=200)
    url = models.URLField(max_length=500)
    secret = models.CharField(max_length=100, blank=True, help_text='Secret for HMAC signature')
    events = models.JSONField(default=list, help_text='List of events to trigger this webhook')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='webhooks')
    created_at = models.DateTimeField(auto_now_add=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    trigger_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    
    # Headers to send with request
    custom_headers = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.url})"
    
    def should_trigger(self, event):
        """Check if webhook should trigger for event"""
        if not self.is_active:
            return False
        return '*' in self.events or event in self.events
    
    def generate_signature(self, payload):
        """Generate HMAC signature for payload"""
        if not self.secret:
            return None
        
        payload_bytes = json.dumps(payload).encode('utf-8')
        signature = hmac.new(
            self.secret.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    def trigger(self, event, data):
        """Trigger the webhook"""
        if not self.should_trigger(event):
            return None
        
        payload = {
            'event': event,
            'timestamp': timezone.now().isoformat(),
            'data': data
        }
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'SmartTaskManager-Webhook/1.0',
            **self.custom_headers
        }
        
        # Add signature if secret is set
        signature = self.generate_signature(payload)
        if signature:
            headers['X-Webhook-Signature'] = signature
        
        try:
            response = requests.post(
                self.url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            # Log the delivery
            WebhookDelivery.objects.create(
                webhook=self,
                event=event,
                payload=payload,
                status_code=response.status_code,
                response_body=response.text[:1000],  # Limit size
                success=response.status_code < 400
            )
            
            # Update webhook stats
            self.last_triggered = timezone.now()
            self.trigger_count += 1
            if response.status_code >= 400:
                self.failure_count += 1
            self.save()
            
            return response
            
        except Exception as e:
            # Log failed delivery
            WebhookDelivery.objects.create(
                webhook=self,
                event=event,
                payload=payload,
                status_code=0,
                response_body=str(e),
                success=False
            )
            
            self.failure_count += 1
            self.save()
            
            return None


class WebhookDelivery(models.Model):
    """Log of webhook deliveries"""
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name='deliveries')
    event = models.CharField(max_length=100)
    payload = models.JSONField()
    status_code = models.IntegerField()
    response_body = models.TextField(blank=True)
    success = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    duration_ms = models.IntegerField(null=True, help_text='Response time in milliseconds')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Webhook Deliveries'
    
    def __str__(self):
        status = 'Success' if self.success else 'Failed'
        return f"{self.webhook.name} - {self.event} ({status})"


class GitHubIntegration(models.Model):
    """GitHub integration settings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='github_integration')
    github_username = models.CharField(max_length=200)
    access_token = models.CharField(max_length=500)  # Encrypted in production
    repositories = models.JSONField(default=list)  # List of connected repos
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'GitHub Integration'
    
    def __str__(self):
        return f"GitHub: {self.github_username}"
    
    def sync_repositories(self):
        """Sync repositories from GitHub"""
        from github import Github
        
        try:
            g = Github(self.access_token)
            user = g.get_user()
            repos = []
            
            for repo in user.get_repos():
                repos.append({
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'url': repo.html_url,
                    'private': repo.private,
                })
            
            self.repositories = repos
            self.last_sync = timezone.now()
            self.save()
            
            return repos
            
        except Exception as e:
            return {'error': str(e)}


class GitHubCommitLink(models.Model):
    """Link GitHub commits to tasks"""
    task = models.ForeignKey('tasks.Task', on_delete=models.CASCADE, related_name='github_commits')
    commit_sha = models.CharField(max_length=40)
    commit_message = models.TextField()
    commit_url = models.URLField()
    repository = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    committed_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-committed_at']
        unique_together = ['task', 'commit_sha']
    
    def __str__(self):
        return f"{self.repository}@{self.commit_sha[:7]} → Task #{self.task.id}"


def trigger_webhooks(event, data):
    """
    Trigger all active webhooks for an event.
    Should be called from signal handlers or views.
    
    Example:
        trigger_webhooks('task.created', {
            'id': task.id,
            'title': task.title,
            'project': task.project.name
        })
    """
    webhooks = Webhook.objects.filter(is_active=True)
    
    for webhook in webhooks:
        if webhook.should_trigger(event):
            # Trigger asynchronously if Celery is available
            try:
                from integrations.tasks import trigger_webhook_async
                trigger_webhook_async.delay(webhook.id, event, data)
            except ImportError:
                # Fallback to synchronous
                webhook.trigger(event, data)
