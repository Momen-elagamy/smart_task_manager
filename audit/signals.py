from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import AuditLog
from django.contrib.auth import get_user_model

User = get_user_model()

def create_audit(action, instance):
    AuditLog.objects.create(
        user=getattr(instance, 'modified_by', None),
        action=action,
        model_name=instance.__class__.__name__,
        object_id=str(instance.pk),
    )

@receiver(post_save)
def model_saved(sender, instance, created, **kwargs):
    if sender.__name__ == 'AuditLog':
        return
    action = "Created" if created else "Updated"
    create_audit(action, instance)

@receiver(post_delete)
def model_deleted(sender, instance, **kwargs):
    if sender.__name__ == 'AuditLog':
        return
    create_audit("Deleted", instance)
