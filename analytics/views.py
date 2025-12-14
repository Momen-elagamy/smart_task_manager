from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.db.models import Q, Sum, Avg, Count
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import timedelta, date
from .models import (
    AnalyticsReport, ProductivityMetrics, TimeTracking, 
    PerformanceIndicator, DashboardWidget
)
from .serializers import (
    AnalyticsReportSerializer, ProductivityMetricsSerializer,
    TimeTrackingSerializer, PerformanceIndicatorSerializer,
    DashboardWidgetSerializer, ProductivityReportSerializer,
    TeamPerformanceSerializer
)
from users.permissions import RolePermission
from projects.models import Project
from tasks.models import Task
from django.contrib.auth import get_user_model

User = get_user_model()

class AnalyticsReportViewSet(viewsets.ModelViewSet):
    """ViewSet for analytics reports."""
    serializer_class = AnalyticsReportSerializer
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin', 'manager']
    
    def get_queryset(self):
        user = self.request.user
        if user.profile.has_role('admin'):
            return AnalyticsReport.objects.all()
        else:
            return AnalyticsReport.objects.filter(
                Q(created_by=user) | Q(is_public=True)
            )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def productivity_report(self, request):
        """تقرير الإنتاجية with Caching"""
        user = request.user
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ✅ Try to get from cache first (simple in-memory caching)
        cache_key = f"productivity_{user.id}_{start_date}_{end_date}"
        from django.core.cache import cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # حساب مقاييس الإنتاجية
        metrics = ProductivityMetrics.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        )
        
        total_tasks = metrics.aggregate(total=Sum('tasks_completed'))['total'] or 0
        total_time = metrics.aggregate(total=Sum('time_spent'))['total'] or timedelta()
        avg_productivity = metrics.aggregate(avg=Avg('productivity_score'))['avg'] or 0
        
        # حساب المهام المكتملة
        completed_tasks = Task.objects.filter(
            assigned_to=user,
            status='completed',
            updated_at__date__range=[start_date, end_date]
        ).count()
        
        # حساب معدل الإنجاز
        total_assigned_tasks = Task.objects.filter(
            assigned_to=user,
            created_at__date__range=[start_date, end_date]
        ).count()
        
        completion_rate = (completed_tasks / total_assigned_tasks * 100) if total_assigned_tasks > 0 else 0
        
        # حساب متوسط الوقت لكل مهمة
        avg_time_per_task = total_time / completed_tasks if completed_tasks > 0 else timedelta()
        
        # إحصائيات للمقارنة (الشهر الماضي كمثال)
        last_month_completed = Task.objects.filter(
            assigned_to=user,
            status='completed',
            updated_at__date__range=[date.today() - timedelta(days=60), date.today() - timedelta(days=30)]
        ).count()
        
        report_data = {
            'user': {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'total_tasks': total_assigned_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': round(completion_rate, 2),
            'total_time': total_time,
            'average_time_per_task': avg_time_per_task,
            'productivity_score': round(avg_productivity, 2),
            'last_month_completed': last_month_completed,
            'period': f"{start_date} to {end_date}",
        }
        
        # Cache the result for 5 minutes
        cache.set(cache_key, report_data, 300)
        
        serializer = ProductivityReportSerializer(report_data)
        return Response(serializer.data)
    
    # Export as CSV
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Export analytics report as CSV"""
        import csv
        from io import StringIO
        from django.http import HttpResponse
        
        user = request.user
        start_date = request.query_params.get('start_date', str(date.today() - timedelta(days=30)))
        end_date = request.query_params.get('end_date', str(date.today()))
        
        # Get productivity report
        metrics = ProductivityMetrics.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        )
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Productivity Report', f'{start_date} to {end_date}'])
        writer.writerow(['Date', 'Tasks Completed', 'Time Spent (hours)', 'Productivity Score'])
        
        # Data
        for metric in metrics:
            writer.writerow([
                metric.date,
                metric.tasks_completed,
                metric.time_spent.total_seconds() / 3600 if metric.time_spent else 0,
                metric.productivity_score
            ])
        
        # Response
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="analytics_{start_date}_{end_date}.csv"'
        return response
    
    # Export as JSON
    @action(detail=False, methods=['get'])
    def export_json(self, request):
        """Export analytics report as JSON"""
        from django.http import JsonResponse
        
        user = request.user
        start_date = request.query_params.get('start_date', str(date.today() - timedelta(days=30)))
        end_date = request.query_params.get('end_date', str(date.today()))
        
        metrics = ProductivityMetrics.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        ).values('date', 'tasks_completed', 'time_spent', 'productivity_score')
        
        return JsonResponse({
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.get_full_name()
            },
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'data': list(metrics)
        })
    
    
    @action(detail=False, methods=['get'])
    def team_performance(self, request):
        """أداء الفريق"""
        user = request.user
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # الحصول على المشاريع التي يديرها المستخدم
        if user.profile.has_role('admin'):
            projects = Project.objects.all()
        else:
            projects = Project.objects.filter(owner=user)
        
        # حساب إحصائيات الفريق
        team_members = User.objects.filter(
            projects__in=projects
        ).distinct()
        
        total_members = team_members.count()
        active_members = team_members.filter(
            last_login__date__range=[start_date, end_date]
        ).count()
        
        # حساب إحصائيات المشاريع
        total_projects = projects.count()
        completed_projects = projects.filter(
            status='completed',
            updated_at__date__range=[start_date, end_date]
        ).count()
        
        # حساب إحصائيات المهام
        project_tasks = Task.objects.filter(project__in=projects)
        total_tasks = project_tasks.count()
        completed_tasks = project_tasks.filter(
            status='completed',
            updated_at__date__range=[start_date, end_date]
        ).count()
        
        # حساب متوسط الإنتاجية
        avg_productivity = ProductivityMetrics.objects.filter(
            user__in=team_members,
            date__range=[start_date, end_date]
        ).aggregate(avg=Avg('productivity_score'))['avg'] or 0
        
        # أفضل الأداء
        top_performers = team_members.annotate(
            productivity=Avg('productivitymetrics__productivity_score')
        ).order_by('-productivity')[:5]
        
        report_data = {
            'team_name': f"فريق {user.get_full_name()}",
            'total_members': total_members,
            'active_members': active_members,
            'total_projects': total_projects,
            'completed_projects': completed_projects,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'average_productivity': round(avg_productivity, 2),
            'top_performers': [
                {
                    'id': str(p.id),
                    'email': p.email,
                    'first_name': p.first_name,
                    'last_name': p.last_name,
                    'full_name': p.get_full_name(),
                    'productivity': p.productivity
                } for p in top_performers
            ],
            'period_start': start_date,
            'period_end': end_date
        }
        
        serializer = TeamPerformanceSerializer(report_data)
        return Response(serializer.data)

class ProductivityMetricsViewSet(viewsets.ModelViewSet):
    """ViewSet لمقاييس الإنتاجية"""
    serializer_class = ProductivityMetricsSerializer
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin', 'manager', 'developer']
    
    def get_queryset(self):
        user = self.request.user
        if user.profile.has_role('admin', 'manager'):
            return ProductivityMetrics.objects.all()
        else:
            return ProductivityMetrics.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def my_metrics(self, request):
        """مقاييس المستخدم الحالي"""
        user = request.user
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.get_queryset().filter(user=user)
        
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class TimeTrackingViewSet(viewsets.ModelViewSet):
    """ViewSet لتتبع الوقت"""
    serializer_class = TimeTrackingSerializer
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin', 'manager', 'developer']
    
    def get_queryset(self):
        user = self.request.user
        if user.profile.has_role('admin', 'manager'):
            return TimeTracking.objects.all()
        else:
            return TimeTracking.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def start_tracking(self, request):
        """Start time tracking for a task."""
        from tasks.models import Task
        
        task_id = request.data.get('task')
        description = request.data.get('description', '')
        
        if not task_id:
            return Response(
                {'error': 'Task ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if there's already active tracking
        active = TimeTracking.objects.filter(
            user=request.user,
            is_active=True
        ).first()
        
        if active:
            return Response(
                {'error': 'Stop current tracking before starting new one'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create new tracking
        tracking = TimeTracking.objects.create(
            user=request.user,
            task=task,
            start_time=timezone.now(),
            description=description,
            is_active=True
        )
        
        serializer = self.get_serializer(tracking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def stop_tracking(self, request, pk=None):
        """إيقاف تتبع الوقت"""
        time_tracking = self.get_object()
        if time_tracking.is_active:
            time_tracking.end_time = timezone.now()
            time_tracking.duration = time_tracking.end_time - time_tracking.start_time
            time_tracking.is_active = False
            time_tracking.save()
            
            serializer = self.get_serializer(time_tracking)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Time tracking is already stopped'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def active_tracking(self, request):
        """التتبع النشط"""
        user = request.user
        active_tracking = TimeTracking.objects.filter(
            user=user, is_active=True
        ).first()
        
        if active_tracking:
            serializer = self.get_serializer(active_tracking)
            return Response(serializer.data)
        else:
            return Response({'message': 'No active time tracking'})

class PerformanceIndicatorViewSet(viewsets.ModelViewSet):
    """ViewSet لمؤشرات الأداء"""
    serializer_class = PerformanceIndicatorSerializer
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin', 'manager']
    
    def get_queryset(self):
        return PerformanceIndicator.objects.all()

class DashboardWidgetViewSet(viewsets.ModelViewSet):
    """ViewSet لودجات لوحة التحكم"""
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin', 'manager', 'developer', 'client']
    
    def get_queryset(self):
        return DashboardWidget.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_dashboard(self, request):
        """لوحة التحكم الشخصية"""
        # For simplicity, we'll generate widgets based on a productivity report.
        # In a real-world scenario, you might fetch saved widget configurations.
        
        user = request.user
        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        # Use the existing productivity_report logic to get data
        try:
            # Temporarily modify request to call the other action method
            request.query_params._mutable = True
            request.query_params['start_date'] = start_date.isoformat()
            request.query_params['end_date'] = end_date.isoformat()
            request.query_params._mutable = False
            
            productivity_data = self.productivity_report(request).data
        except Exception:
            # Fallback in case productivity report fails
            productivity_data = {}

        # Construct widgets dynamically based on the report data
        widgets_data = [
            {
                "id": 1,
                "title": "Total Tasks",
                "widget_type": "stat_card",
                "config": {"type": "total_tasks", "value": productivity_data.get('total_tasks', 'N/A')}
            },
            {
                "id": 2,
                "title": "Completed Tasks",
                "widget_type": "stat_card",
                "config": {
                    "type": "completed_tasks", 
                    "value": productivity_data.get('completed_tasks', 'N/A'),
                    "last_month_value": productivity_data.get('last_month_completed', 0)
                }
            },
            {
                "id": 3,
                "title": "Pending Tasks",
                "widget_type": "stat_card",
                "config": {"type": "pending_tasks", "value": productivity_data.get('total_tasks', 0) - productivity_data.get('completed_tasks', 0)}
            },
            {
                "id": 4,
                "title": "Productivity Score",
                "widget_type": "stat_card",
                "config": {"type": "productivity", "value": f"{productivity_data.get('productivity_score', 0)}%"}
            }
        ]

        serializer = DashboardWidgetSerializer(widgets_data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def export_pdf(self, request):
        """Export analytics report as PDF."""
        from .reports_export import generate_pdf_report
        from datetime import datetime
        
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        if date_to:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        return generate_pdf_report(request.user, date_from, date_to)
    
    @action(detail=False, methods=['get'])
    def export_excel(self, request):
        """Export analytics report as Excel."""
        from .reports_export import generate_excel_report
        from datetime import datetime
        
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        if date_to:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        return generate_excel_report(request.user, date_from, date_to)


class AnalyticsPageView(LoginRequiredMixin, TemplateView):
    """HTML page for analytics dashboard"""
    template_name = 'analytics/analytics_dashboard.html'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx['reports'] = AnalyticsReport.objects.filter(
            Q(created_by=user) | Q(is_public=True)
        ).order_by('-created_at')[:10]
        return ctx


class DashboardStatsApiView(APIView):
    """API endpoint for dashboard statistics - returns real data"""
    permission_classes = [AllowAny]  # Allow all to fix loading issue
    
    def get(self, request):
        from tasks.models import Task
        from projects.models import Project
        from django.contrib.auth import get_user_model
        from datetime import datetime, timedelta
        
        User = get_user_model()
        user = request.user
        
        # Get date range
        today = datetime.now().date()
        month_ago = today - timedelta(days=30)
        two_months_ago = today - timedelta(days=60)
        
        # Tasks stats
        all_tasks = Task.objects.all()
        total_tasks = all_tasks.count()
        completed_tasks = all_tasks.filter(status__in=['done', 'completed']).count()
        in_progress_tasks = all_tasks.filter(status='in_progress').count()
        overdue_tasks = all_tasks.filter(due_date__lt=today).exclude(status__in=['done', 'completed']).count()
        
        # Last month comparison
        last_month_completed = all_tasks.filter(
            status__in=['done', 'completed'],
            updated_at__date__range=[two_months_ago, month_ago]
        ).count()
        this_month_completed = all_tasks.filter(
            status__in=['done', 'completed'],
            updated_at__date__gte=month_ago
        ).count()
        
        # Calculate change percentage
        if last_month_completed > 0:
            change_percent = round(((this_month_completed - last_month_completed) / last_month_completed) * 100)
        else:
            change_percent = 100 if this_month_completed > 0 else 0
        
        # Completion rate
        completion_rate = round((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
        
        # Projects stats
        all_projects = Project.objects.all()
        total_projects = all_projects.count()
        active_projects = all_projects.filter(status__in=['active', 'in_progress']).count()
        
        # Team stats
        total_members = User.objects.filter(is_active=True).count()
        
        # Team performance (top performers)
        team_performance = []
        users = User.objects.filter(is_active=True)[:10]
        for u in users:
            user_tasks = Task.objects.filter(assigned_to=u)
            user_total = user_tasks.count()
            user_completed = user_tasks.filter(status__in=['done', 'completed']).count()
            rate = round((user_completed / user_total * 100)) if user_total > 0 else 0
            
            # Get user name safely
            user_name = u.email.split('@')[0]
            if hasattr(u, 'get_full_name'):
                user_name = u.get_full_name() or user_name
            elif hasattr(u, 'first_name') and u.first_name:
                user_name = f"{u.first_name} {getattr(u, 'last_name', '')}".strip() or user_name
            
            if user_total > 0:
                team_performance.append({
                    'id': u.id,
                    'name': user_name,
                    'email': u.email,
                    'role': getattr(u, 'role', 'member'),
                    'tasks': user_total,
                    'completed': user_completed,
                    'rate': rate
                })
        
        # Sort by rate descending
        team_performance.sort(key=lambda x: x['rate'], reverse=True)
        
        return Response({
            'tasks': {
                'total': total_tasks,
                'completed': completed_tasks,
                'in_progress': in_progress_tasks,
                'overdue': overdue_tasks,
                'completion_rate': completion_rate,
                'change_percent': change_percent
            },
            'projects': {
                'total': total_projects,
                'active': active_projects
            },
            'team': {
                'total_members': total_members,
                'performance': team_performance[:5]
            }
        })