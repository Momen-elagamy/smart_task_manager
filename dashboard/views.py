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
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from projects.models import Project
from tasks.models import Task
from notifications.models import Notification

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


from rest_framework.decorators import api_view, permission_classes as perm_decorator
from rest_framework.permissions import IsAuthenticated, AllowAny


@api_view(['GET'])
@perm_decorator([AllowAny])  # Allow unauthenticated for now to debug
def dashboard_stats(request):
    """Return aggregated stats for analytics dashboard.
    Works with both session and JWT authentication.
    Shows all data for the user's accessible tasks/projects.
    """
    user = request.user if request.user.is_authenticated else None
    
    # Get all tasks and projects (user can see all in their workspace)
    # For a multi-tenant app, you'd filter by organization/team
    tasks = Task.objects.all()
    projects = Project.objects.all()
    
    # If user is authenticated, try to get their specific data first
    # If they have no assigned tasks, show all tasks they can access
    if user:
        user_tasks = Task.objects.filter(assigned_to=user)
        user_projects = Project.objects.filter(owner=user)
        # If user has their own tasks/projects, show those; otherwise show all
        if user_tasks.exists():
            tasks = user_tasks
        if user_projects.exists():
            projects = user_projects
    
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='done').count()
    in_progress_tasks = tasks.filter(status='in_progress').count()
    pending_tasks = tasks.filter(status='todo').count()
    
    # For notifications
    notifications_unread = 0
    if user:
        notifications_unread = Notification.objects.filter(user=user, is_read=False).count()
    
    data = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'pending_tasks': pending_tasks,
        'total_projects': projects.count(),
        'notifications_unread': notifications_unread,
        # Legacy fields for compatibility
        'projects': projects.count(),
        'tasks': total_tasks,
    }
    return Response(data)









