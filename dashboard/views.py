from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Dashboard, DashboardWidget, DashboardFilter, DashboardShare
from .serializers import (
    DashboardSerializer, DashboardWidgetSerializer,
    DashboardFilterSerializer, DashboardShareSerializer
)
from users.permissions import RolePermission

class DashboardViewSet(viewsets.ModelViewSet):
    """ViewSet للوحات التحكم"""
    serializer_class = DashboardSerializer
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin', 'manager', 'developer', 'client']
    
    def get_queryset(self):
        user = self.request.user
        return Dashboard.objects.filter(
            Q(user=user) | Q(is_public=True) | Q(dashboardshare__shared_with=user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """مشاركة لوحة التحكم"""
        dashboard = self.get_object()
        shared_with_email = request.data.get('shared_with')
        permission_level = request.data.get('permission_level', 'view')
        
        if not shared_with_email:
            return Response(
                {'error': 'shared_with is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            shared_with_user = User.objects.get(email=shared_with_email)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        share, created = DashboardShare.objects.get_or_create(
            dashboard=dashboard,
            shared_with=shared_with_user,
            defaults={
                'permission_level': permission_level,
                'shared_by': request.user
            }
        )
        
        if not created:
            share.permission_level = permission_level
            share.save()
        
        serializer = DashboardShareSerializer(share)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_dashboards(self, request):
        """لوحات التحكم الشخصية"""
        dashboards = Dashboard.objects.filter(user=request.user)
        serializer = self.get_serializer(dashboards, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def shared_with_me(self, request):
        """لوحات التحكم المشتركة معي"""
        dashboards = Dashboard.objects.filter(
            dashboardshare__shared_with=request.user
        )
        serializer = self.get_serializer(dashboards, many=True)
        return Response(serializer.data)

class DashboardWidgetViewSet(viewsets.ModelViewSet):
    """ViewSet لودجات لوحة التحكم"""
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin', 'manager', 'developer', 'client']
    
    def get_queryset(self):
        dashboard_id = self.request.query_params.get('dashboard')
        if dashboard_id:
            return DashboardWidget.objects.filter(dashboard_id=dashboard_id)
        return DashboardWidget.objects.filter(dashboard__user=self.request.user)
    
    def perform_create(self, serializer):
        dashboard_id = self.request.data.get('dashboard')
        if dashboard_id:
            dashboard = Dashboard.objects.get(id=dashboard_id)
            serializer.save(dashboard=dashboard)
    
    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        """نقل الودجة"""
        widget = self.get_object()
        position_x = request.data.get('position_x')
        position_y = request.data.get('position_y')
        
        if position_x is not None:
            widget.position_x = position_x
        if position_y is not None:
            widget.position_y = position_y
        
        widget.save()
        serializer = self.get_serializer(widget)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resize(self, request, pk=None):
        """تغيير حجم الودجة"""
        widget = self.get_object()
        width = request.data.get('width')
        height = request.data.get('height')
        
        if width is not None:
            widget.width = width
        if height is not None:
            widget.height = height
        
        widget.save()
        serializer = self.get_serializer(widget)
        return Response(serializer.data)

class DashboardFilterViewSet(viewsets.ModelViewSet):
    """ViewSet لمرشحات لوحة التحكم"""
    serializer_class = DashboardFilterSerializer
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin', 'manager', 'developer', 'client']
    
    def get_queryset(self):
        dashboard_id = self.request.query_params.get('dashboard')
        if dashboard_id:
            return DashboardFilter.objects.filter(dashboard_id=dashboard_id)
        return DashboardFilter.objects.filter(dashboard__user=self.request.user)
    
    def perform_create(self, serializer):
        dashboard_id = self.request.data.get('dashboard')
        if dashboard_id:
            dashboard = Dashboard.objects.get(id=dashboard_id)
            serializer.save(dashboard=dashboard)









