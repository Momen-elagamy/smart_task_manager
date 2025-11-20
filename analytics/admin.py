from django.contrib import admin
from .models import (
    AnalyticsReport, ProductivityMetrics, TimeTracking,
    PerformanceIndicator, DashboardWidget
)

@admin.register(AnalyticsReport)
class AnalyticsReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'created_by', 'is_public', 'created_at']
    list_filter = ['report_type', 'is_public', 'created_at']
    search_fields = ['name', 'description', 'created_by__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']

@admin.register(ProductivityMetrics)
class ProductivityMetricsAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'tasks_completed', 'productivity_score', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'created_at']
    ordering = ['-date']

@admin.register(TimeTracking)
class TimeTrackingAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'start_time', 'end_time', 'duration', 'is_active']
    list_filter = ['is_active', 'start_time', 'created_at']
    search_fields = ['user__email', 'task__title', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-start_time']

@admin.register(PerformanceIndicator)
class PerformanceIndicatorAdmin(admin.ModelAdmin):
    list_display = ['name', 'metric_type', 'target_value', 'current_value', 'unit']
    list_filter = ['metric_type', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['name']

@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'widget_type', 'user', 'position_x', 'position_y', 'is_visible']
    list_filter = ['widget_type', 'is_visible', 'created_at']
    search_fields = ['name', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['user', 'position_y', 'position_x']