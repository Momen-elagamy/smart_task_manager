from django.core.mail import send_mail
from django.conf import settings
from pyfcm import FCMNotification
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_email_notification(subject, message, to_email):
    """
    Sends an email notification asynchronously.
    """
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [to_email],
            fail_silently=False,
        )
        logger.info(f"Email notification sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")

@shared_task
def send_push_notification(registration_id, message_title, message_body, data_message=None):
    """
    Sends a push notification to a single device asynchronously.
    """
    if not registration_id or not settings.FCM_SERVER_KEY:
        return

    try:
        push_service = FCMNotification(api_key=settings.FCM_SERVER_KEY)
        result = push_service.notify_single_device(
            registration_id=registration_id, message_title=message_title, message_body=message_body, data_message=data_message)
        logger.info(f"Push notification sent to {registration_id}. Result: {result}")
    except Exception as e:
        logger.error(f"Failed to send push notification to {registration_id}: {e}")
