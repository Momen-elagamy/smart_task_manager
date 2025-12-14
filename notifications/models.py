import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
	NOTIFICATION_TYPE_CHOICES = (
		('email', 'Email'),
		('push', 'Push Notification'),
		('web', 'Web Notification'),
	)

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notifications', on_delete=models.CASCADE)
	message = models.TextField()
	is_read = models.BooleanField(default=False)
	notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPE_CHOICES, default='web')
	task = models.ForeignKey('tasks.Task', related_name='notifications', on_delete=models.CASCADE, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"Notification({self.notification_type}) to {self.user.email}"[:80]

	def mark_read(self):
		if not self.is_read:
			self.is_read = True
			self.save(update_fields=['is_read'])


class UserFCMToken(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='fcm_token', on_delete=models.CASCADE)
	token = models.CharField(max_length=255, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"FCMToken for {self.user.email}"[:60]


# Simple realtime helper referenced by signals
def send_realtime_notification(user_id, message):
	"""Send a minimal realtime notification via channels layer if available.
	Falls back silently if channels not configured."""
	try:
		from channels.layers import get_channel_layer
		from asgiref.sync import async_to_sync
		layer = get_channel_layer()
		if layer:
			async_to_sync(layer.group_send)(
				f"user_{user_id}",
				{"type": "notify.message", "message": message, "timestamp": timezone.now().isoformat()}
			)
	except Exception:
		# Silently ignore in absence of channels setup
		pass
