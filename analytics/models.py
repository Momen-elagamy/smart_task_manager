from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from projects.models import Project
from tasks.models import Task
import uuid

User = get_user_model()

class AnalyticsReport(models.Model):
    """نموذج التقارير التحليلية"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="اسم التقرير")
    description = models.TextField(blank=True, verbose_name="وصف التقرير")
    report_type = models.CharField(
        max_length=50,
        choices=[
            ('productivity', 'تقرير الإنتاجية'),
            ('performance', 'تقرير الأداء'),
            ('time_tracking', 'تتبع الوقت'),
            ('cost_analysis', 'تحليل التكلفة'),
            ('team_performance', 'أداء الفريق'),
        ],
        verbose_name="نوع التقرير"
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="أنشأ بواسطة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    is_public = models.BooleanField(default=False, verbose_name="عام")
    
    class Meta:
        verbose_name = "تقرير تحليلي"
        verbose_name_plural = "التقارير التحليلية"
        ordering = ['-created_at']

class ProductivityMetrics(models.Model):
    """مقاييس الإنتاجية"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, verbose_name="المشروع")
    date = models.DateField(verbose_name="التاريخ")
    
    # مقاييس الإنتاجية
    tasks_completed = models.IntegerField(default=0, verbose_name="المهام المكتملة")
    tasks_created = models.IntegerField(default=0, verbose_name="المهام المنشأة")
    time_spent = models.DurationField(default=timezone.timedelta, verbose_name="الوقت المستغرق")
    productivity_score = models.FloatField(default=0.0, verbose_name="نقاط الإنتاجية")
    
    # مقاييس إضافية
    comments_count = models.IntegerField(default=0, verbose_name="عدد التعليقات")
    attachments_count = models.IntegerField(default=0, verbose_name="عدد المرفقات")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    
    class Meta:
        verbose_name = "مقياس إنتاجية"
        verbose_name_plural = "مقاييس الإنتاجية"
        unique_together = ['user', 'date', 'project']
        ordering = ['-date']

class TimeTracking(models.Model):
    """تتبع الوقت"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name="المهمة")
    start_time = models.DateTimeField(verbose_name="وقت البداية")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="وقت النهاية")
    duration = models.DurationField(null=True, blank=True, verbose_name="المدة")
    description = models.TextField(blank=True, verbose_name="وصف العمل")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "تتبع الوقت"
        verbose_name_plural = "تتبع الوقت"
        ordering = ['-start_time']

class PerformanceIndicator(models.Model):
    """مؤشرات الأداء"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="اسم المؤشر")
    description = models.TextField(blank=True, verbose_name="وصف المؤشر")
    metric_type = models.CharField(
        max_length=50,
        choices=[
            ('completion_rate', 'معدل الإنجاز'),
            ('time_efficiency', 'كفاءة الوقت'),
            ('quality_score', 'نقاط الجودة'),
            ('collaboration', 'التعاون'),
            ('innovation', 'الابتكار'),
        ],
        verbose_name="نوع المؤشر"
    )
    target_value = models.FloatField(verbose_name="القيمة المستهدفة")
    current_value = models.FloatField(default=0.0, verbose_name="القيمة الحالية")
    unit = models.CharField(max_length=20, verbose_name="الوحدة")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "مؤشر أداء"
        verbose_name_plural = "مؤشرات الأداء"
        ordering = ['name']

class DashboardWidget(models.Model):
    """ودجات لوحة التحكم"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="اسم الودجة")
    widget_type = models.CharField(
        max_length=50,
        choices=[
            ('chart', 'رسم بياني'),
            ('metric', 'مقياس'),
            ('table', 'جدول'),
            ('progress', 'شريط تقدم'),
            ('list', 'قائمة'),
        ],
        verbose_name="نوع الودجة"
    )
    data_source = models.CharField(max_length=100, verbose_name="مصدر البيانات")
    position_x = models.IntegerField(default=0, verbose_name="الموقع X")
    position_y = models.IntegerField(default=0, verbose_name="الموقع Y")
    width = models.IntegerField(default=4, verbose_name="العرض")
    height = models.IntegerField(default=3, verbose_name="الارتفاع")
    is_visible = models.BooleanField(default=True, verbose_name="مرئي")
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "ودجة لوحة التحكم"
        verbose_name_plural = "ودجات لوحة التحكم"
        ordering = ['position_y', 'position_x']