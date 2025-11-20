from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class ChatRoom(models.Model):
    """نموذج غرف الدردشة"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="اسم الغرفة")
    description = models.TextField(blank=True, verbose_name="وصف الغرفة")
    room_type = models.CharField(
        max_length=20,
        choices=[
            ('project', 'غرفة المشروع'),
            ('team', 'غرفة الفريق'),
            ('general', 'عامة'),
            ('private', 'خاصة'),
        ],
        default='general',
        verbose_name="نوع الغرفة"
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="أنشأ بواسطة")
    members = models.ManyToManyField(User, related_name='chat_rooms', verbose_name="الأعضاء")
    is_active = models.BooleanField(default=True, verbose_name="نشطة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "غرفة دردشة"
        verbose_name_plural = "غرف الدردشة"
        ordering = ['-created_at']

class ChatMessage(models.Model):
    """نموذج رسائل الدردشة"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, verbose_name="الغرفة")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المرسل")
    content = models.TextField(verbose_name="محتوى الرسالة")
    message_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'نص'),
            ('image', 'صورة'),
            ('file', 'ملف'),
            ('system', 'نظام'),
        ],
        default='text',
        verbose_name="نوع الرسالة"
    )
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True, verbose_name="مرفق")
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="رد على")
    is_edited = models.BooleanField(default=False, verbose_name="تم التعديل")
    is_deleted = models.BooleanField(default=False, verbose_name="تم الحذف")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإرسال")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "رسالة دردشة"
        verbose_name_plural = "رسائل الدردشة"
        ordering = ['-created_at']

class MessageReaction(models.Model):
    """نموذج تفاعلات الرسائل"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, verbose_name="الرسالة")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    reaction_type = models.CharField(
        max_length=20,
        choices=[
            ('like', 'إعجاب'),
            ('love', 'حب'),
            ('laugh', 'ضحك'),
            ('angry', 'غضب'),
            ('sad', 'حزن'),
            ('wow', 'دهشة'),
        ],
        verbose_name="نوع التفاعل"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التفاعل")
    
    class Meta:
        verbose_name = "تفاعل رسالة"
        verbose_name_plural = "تفاعلات الرسائل"
        unique_together = ['message', 'user', 'reaction_type']
        ordering = ['-created_at']

class ChatNotification(models.Model):
    """نموذج إشعارات الدردشة"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, verbose_name="الغرفة")
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, verbose_name="الرسالة")
    is_read = models.BooleanField(default=False, verbose_name="تم القراءة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإشعار")
    
    class Meta:
        verbose_name = "إشعار دردشة"
        verbose_name_plural = "إشعارات الدردشة"
        unique_together = ['user', 'message']
        ordering = ['-created_at']










