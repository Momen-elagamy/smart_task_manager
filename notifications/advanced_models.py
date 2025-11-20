from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class NotificationTemplate(models.Model):
    """نموذج قوالب الإشعارات"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="اسم القالب")
    title_template = models.CharField(max_length=200, verbose_name="قالب العنوان")
    message_template = models.TextField(verbose_name="قالب الرسالة")
    notification_type = models.CharField(
        max_length=50,
        choices=[
            ('task_assigned', 'تعيين مهمة'),
            ('task_completed', 'إكمال مهمة'),
            ('task_due', 'موعد مهمة'),
            ('comment_added', 'إضافة تعليق'),
            ('mention', 'إشارة'),
            ('project_update', 'تحديث مشروع'),
            ('system', 'نظام'),
        ],
        verbose_name="نوع الإشعار"
    )
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "قالب إشعار"
        verbose_name_plural = "قوالب الإشعارات"
        ordering = ['name']

class NotificationChannel(models.Model):
    """نموذج قنوات الإشعارات"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    channel_type = models.CharField(
        max_length=20,
        choices=[
            ('email', 'البريد الإلكتروني'),
            ('sms', 'رسالة نصية'),
            ('push', 'إشعار محمول'),
            ('web', 'إشعار ويب'),
            ('slack', 'Slack'),
            ('discord', 'Discord'),
        ],
        verbose_name="نوع القناة"
    )
    is_enabled = models.BooleanField(default=True, verbose_name="مفعل")
    settings = models.JSONField(default=dict, verbose_name="الإعدادات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "قناة إشعار"
        verbose_name_plural = "قنوات الإشعارات"
        unique_together = ['user', 'channel_type']
        ordering = ['user', 'channel_type']

class NotificationRule(models.Model):
    """نموذج قواعد الإشعارات"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    name = models.CharField(max_length=100, verbose_name="اسم القاعدة")
    description = models.TextField(blank=True, verbose_name="وصف القاعدة")
    trigger_event = models.CharField(
        max_length=50,
        choices=[
            ('task_created', 'إنشاء مهمة'),
            ('task_updated', 'تحديث مهمة'),
            ('task_completed', 'إكمال مهمة'),
            ('task_due', 'موعد مهمة'),
            ('comment_added', 'إضافة تعليق'),
            ('mention', 'إشارة'),
            ('project_created', 'إنشاء مشروع'),
            ('project_updated', 'تحديث مشروع'),
        ],
        verbose_name="حدث التفعيل"
    )
    conditions = models.JSONField(default=dict, verbose_name="الشروط")
    channels = models.ManyToManyField(NotificationChannel, verbose_name="القنوات")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "قاعدة إشعار"
        verbose_name_plural = "قواعد الإشعارات"
        ordering = ['user', 'name']

class NotificationLog(models.Model):
    """نموذج سجل الإشعارات"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    notification = models.ForeignKey('notifications.Notification', on_delete=models.CASCADE, verbose_name="الإشعار")
    channel = models.ForeignKey(NotificationChannel, on_delete=models.CASCADE, verbose_name="القناة")
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'في الانتظار'),
            ('sent', 'تم الإرسال'),
            ('delivered', 'تم التسليم'),
            ('failed', 'فشل'),
            ('read', 'تم القراءة'),
        ],
        default='pending',
        verbose_name="الحالة"
    )
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الإرسال")
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت التسليم")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت القراءة")
    error_message = models.TextField(blank=True, verbose_name="رسالة الخطأ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    
    class Meta:
        verbose_name = "سجل إشعار"
        verbose_name_plural = "سجلات الإشعارات"
        ordering = ['-created_at']

class EmailTemplate(models.Model):
    """نموذج قوالب البريد الإلكتروني"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="اسم القالب")
    subject = models.CharField(max_length=200, verbose_name="الموضوع")
    html_content = models.TextField(verbose_name="محتوى HTML")
    text_content = models.TextField(verbose_name="محتوى نصي")
    notification_type = models.CharField(max_length=50, verbose_name="نوع الإشعار")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "قالب بريد إلكتروني"
        verbose_name_plural = "قوالب البريد الإلكتروني"
        ordering = ['name']

class SlackIntegration(models.Model):
    """نموذج تكامل Slack"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    workspace_name = models.CharField(max_length=100, verbose_name="اسم مساحة العمل")
    channel_name = models.CharField(max_length=100, verbose_name="اسم القناة")
    webhook_url = models.URLField(verbose_name="رابط Webhook")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "تكامل Slack"
        verbose_name_plural = "تكاملات Slack"
        ordering = ['user', 'workspace_name']










