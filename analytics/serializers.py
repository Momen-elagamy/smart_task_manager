from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    AnalyticsReport, ProductivityMetrics, TimeTracking,
    PerformanceIndicator, DashboardWidget
)
from projects.models import Project
from tasks.models import Task

User = get_user_model()

class AnalyticsReportSerializer(serializers.ModelSerializer):
    """Serializer للتقارير التحليلية"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = AnalyticsReport
        fields = [
            'id', 'name', 'description', 'report_type', 'created_by',
            'created_by_name', 'created_at', 'updated_at', 'is_public'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ProductivityMetricsSerializer(serializers.ModelSerializer):
    """Serializer لمقاييس الإنتاجية"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = ProductivityMetrics
        fields = [
            'id', 'user', 'user_name', 'project', 'project_name', 'date',
            'tasks_completed', 'tasks_created', 'time_spent', 'productivity_score',
            'comments_count', 'attachments_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class TimeTrackingSerializer(serializers.ModelSerializer):
    """Serializer لتتبع الوقت"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    project_name = serializers.CharField(source='task.project.name', read_only=True)
    
    class Meta:
        model = TimeTracking
        fields = [
            'id', 'user', 'user_name', 'task', 'task_title', 'project_name',
            'start_time', 'end_time', 'duration', 'description', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class PerformanceIndicatorSerializer(serializers.ModelSerializer):
    """Serializer لمؤشرات الأداء"""
    
    class Meta:
        model = PerformanceIndicator
        fields = [
            'id', 'name', 'description', 'metric_type', 'target_value',
            'current_value', 'unit', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class DashboardWidgetSerializer(serializers.ModelSerializer):
    """Serializer لودجات لوحة التحكم"""
    
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'name', 'widget_type', 'data_source', 'position_x',
            'position_y', 'width', 'height', 'is_visible', 'user',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ProductivityReportSerializer(serializers.Serializer):
    """Serializer لتقرير الإنتاجية"""
    user = serializers.DictField()
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    total_time = serializers.DurationField()
    average_time_per_task = serializers.DurationField()
    productivity_score = serializers.FloatField()
    period_start = serializers.DateField()
    period_end = serializers.DateField()

class TeamPerformanceSerializer(serializers.Serializer):
    """Serializer لأداء الفريق"""
    team_name = serializers.CharField()
    total_members = serializers.IntegerField()
    active_members = serializers.IntegerField()
    total_projects = serializers.IntegerField()
    completed_projects = serializers.IntegerField()
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    average_productivity = serializers.FloatField()
    top_performers = serializers.ListField(child=serializers.DictField())
    period_start = serializers.DateField()
    period_end = serializers.DateField()








