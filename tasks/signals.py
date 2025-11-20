from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task
from notifications.models import Notification
from notifications.utils import send_email_notification, send_push_notification # This will now import Celery tasks
from asgiref.sync import async_to_sync
import json

@receiver(post_save, sender=Task)
def create_task_notification(sender, instance, created, **kwargs):
    layer = get_channel_layer()
    if not instance.assigned_to:
        return

    user = instance.assigned_to
    message = ""
    subject = ""

    if created:
        subject = f"New Task Assigned: {instance.title}"
        message = f"A new task '{instance.title}' has been assigned to you."
    else:
        subject = f"Task Update: {instance.title}"
        message = f"The task '{instance.title}' status has been updated to '{instance.get_status_display()}'."

    # 1. Create Web Notification in DB
    Notification.objects.create(user=user, message=message, task=instance, notification_type='web')

    # 2. Send Real-time (WebSocket) Notification
    from notifications.models import send_realtime_notification
    send_realtime_notification(user.id, message)

    # 3. Send Email Notification
    if user.email:
        send_email_notification.delay(
            subject=subject,
            message=message,
            to_email=user.email
        )

    # 4. Send Push Notification (Asynchronously)
    try:
        if hasattr(user, 'fcm_token') and user.fcm_token.token:
            send_push_notification.delay(
                registration_id=user.fcm_token.token,
                message_title=subject,
                message_body=message,
                data_message={"task_id": str(instance.id), "project_id": str(instance.project.id)}
            )
    except Exception as e:
        # Avoid crashing if fcm_token doesn't exist or is invalid.
        # The error will be logged inside the Celery task.
        logger.warning(f"Could not queue push notification for user {user.id}: {e}")
