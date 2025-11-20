from rest_framework import serializers
from .models import Dashboard, DashboardWidget, DashboardFilter, DashboardShare

class DashboardSerializer(serializers.ModelSerializer):
    """سيرياليزر لوحة التحكم"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    widgets_count = serializers.SerializerMethodField()
    filters_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Dashboard
        fields = [
            'id', 'name', 'description', 'user', 'user_email', 'user_name',
            'is_default', 'is_public', 'layout', 'settings', 'widgets_count',
            'filters_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_widgets_count(self, obj):
        return obj.dashboardwidget_set.count()
    
    def get_filters_count(self, obj):
        return obj.dashboardfilter_set.count()

class DashboardWidgetSerializer(serializers.ModelSerializer):
    """سيرياليزر ودجة لوحة التحكم"""
    dashboard_name = serializers.CharField(source='dashboard.name', read_only=True)
    
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'dashboard', 'dashboard_name', 'widget_type', 'title',
            'description', 'data_source', 'data_config', 'position_x',
            'position_y', 'width', 'height', 'is_visible', 'refresh_interval',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class DashboardFilterSerializer(serializers.ModelSerializer):
    """سيرياليزر مرشح لوحة التحكم"""
    dashboard_name = serializers.CharField(source='dashboard.name', read_only=True)
    
    class Meta:
        model = DashboardFilter
        fields = [
            'id', 'dashboard', 'dashboard_name', 'name', 'filter_type',
            'field_name', 'default_value', 'options', 'is_required',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class DashboardShareSerializer(serializers.ModelSerializer):
    """سيرياليزر مشاركة لوحة التحكم"""
    shared_with_email = serializers.CharField(source='shared_with.email', read_only=True)
    shared_with_name = serializers.CharField(source='shared_with.get_full_name', read_only=True)
    shared_by_email = serializers.CharField(source='shared_by.email', read_only=True)
    shared_by_name = serializers.CharField(source='shared_by.get_full_name', read_only=True)
    dashboard_name = serializers.CharField(source='dashboard.name', read_only=True)
    
    class Meta:
        model = DashboardShare
        fields = [
            'id', 'dashboard', 'dashboard_name', 'shared_with', 'shared_with_email',
            'shared_with_name', 'permission_level', 'shared_by', 'shared_by_email',
            'shared_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
