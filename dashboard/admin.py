from django.contrib import admin
from .models import Dashboard, DashboardWidget, DashboardFilter, DashboardShare

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_default', 'is_public', 'created_at']
    list_filter = ['is_default', 'is_public', 'created_at']
    search_fields = ['name', 'description', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']

@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ['title', 'widget_type', 'dashboard', 'position_x', 'position_y', 'is_visible']
    list_filter = ['widget_type', 'is_visible', 'created_at']
    search_fields = ['title', 'dashboard__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['dashboard', 'position_y', 'position_x']

@admin.register(DashboardFilter)
class DashboardFilterAdmin(admin.ModelAdmin):
    list_display = ['name', 'filter_type', 'dashboard', 'is_required', 'created_at']
    list_filter = ['filter_type', 'is_required', 'created_at']
    search_fields = ['name', 'dashboard__name']
    readonly_fields = ['id', 'created_at']
    ordering = ['dashboard', 'name']

@admin.register(DashboardShare)
class DashboardShareAdmin(admin.ModelAdmin):
    list_display = ['dashboard', 'shared_with', 'permission_level', 'shared_by', 'created_at']
    list_filter = ['permission_level', 'created_at']
    search_fields = ['dashboard__name', 'shared_with__email', 'shared_by__email']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']









