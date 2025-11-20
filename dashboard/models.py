from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class Dashboard(models.Model):
    """نموذج لوحة التحكم"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="اسم لوحة التحكم")
    description = models.TextField(blank=True, verbose_name="وصف لوحة التحكم")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    is_default = models.BooleanField(default=False, verbose_name="افتراضية")
    is_public = models.BooleanField(default=False, verbose_name="عامة")
    layout = models.JSONField(default=dict, verbose_name="تخطيط")
    settings = models.JSONField(default=dict, verbose_name="الإعدادات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "لوحة تحكم"
        verbose_name_plural = "لوحات التحكم"
        ordering = ['-created_at']

class DashboardWidget(models.Model):
    """نموذج ودجات لوحة التحكم"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, verbose_name="لوحة التحكم")
    widget_type = models.CharField(
        max_length=50,
        choices=[
            ('chart', 'رسم بياني'),
            ('metric', 'مقياس'),
            ('table', 'جدول'),
            ('progress', 'شريط تقدم'),
            ('list', 'قائمة'),
            ('calendar', 'تقويم'),
            ('timeline', 'الخط الزمني'),
            ('gauge', 'مقياس'),
            ('pie', 'دائري'),
            ('bar', 'عمودي'),
            ('line', 'خطي'),
        ],
        verbose_name="نوع الودجة"
    )
    title = models.CharField(max_length=100, verbose_name="عنوان الودجة")
    description = models.TextField(blank=True, verbose_name="وصف الودجة")
    data_source = models.CharField(max_length=100, verbose_name="مصدر البيانات")
    data_config = models.JSONField(default=dict, verbose_name="إعدادات البيانات")
    position_x = models.IntegerField(default=0, verbose_name="الموقع X")
    position_y = models.IntegerField(default=0, verbose_name="الموقع Y")
    width = models.IntegerField(default=4, verbose_name="العرض")
    height = models.IntegerField(default=3, verbose_name="الارتفاع")
    is_visible = models.BooleanField(default=True, verbose_name="مرئي")
    refresh_interval = models.IntegerField(default=0, verbose_name="فترة التحديث (ثواني)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "ودجة لوحة التحكم"
        verbose_name_plural = "ودجات لوحة التحكم"
        ordering = ['position_y', 'position_x']

class DashboardFilter(models.Model):
    """نموذج مرشحات لوحة التحكم"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, verbose_name="لوحة التحكم")
    name = models.CharField(max_length=100, verbose_name="اسم المرشح")
    filter_type = models.CharField(
        max_length=20,
        choices=[
            ('date_range', 'نطاق تاريخ'),
            ('user', 'مستخدم'),
            ('project', 'مشروع'),
            ('status', 'حالة'),
            ('priority', 'أولوية'),
        ],
        verbose_name="نوع المرشح"
    )
    field_name = models.CharField(max_length=100, verbose_name="اسم الحقل")
    default_value = models.CharField(max_length=200, blank=True, verbose_name="القيمة الافتراضية")
    options = models.JSONField(default=list, verbose_name="الخيارات")
    is_required = models.BooleanField(default=False, verbose_name="مطلوب")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    
    class Meta:
        verbose_name = "مرشح لوحة التحكم"
        verbose_name_plural = "مرشحات لوحة التحكم"
        ordering = ['name']

class DashboardShare(models.Model):
    """نموذج مشاركة لوحة التحكم"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, verbose_name="لوحة التحكم")
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="مشارك مع")
    permission_level = models.CharField(
        max_length=20,
        choices=[
            ('view', 'عرض فقط'),
            ('edit', 'تعديل'),
            ('admin', 'إدارة'),
        ],
        default='view',
        verbose_name="مستوى الصلاحية"
    )
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_dashboards', verbose_name="مشارك بواسطة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ المشاركة")
    
    class Meta:
        verbose_name = "مشاركة لوحة التحكم"
        verbose_name_plural = "مشاركات لوحة التحكم"
        unique_together = ['dashboard', 'shared_with']
        ordering = ['-created_at']










