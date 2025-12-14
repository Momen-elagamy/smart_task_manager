from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AnalyticsReportViewSet, ProductivityMetricsViewSet,
    TimeTrackingViewSet, PerformanceIndicatorViewSet,
    DashboardWidgetViewSet, AnalyticsPageView, DashboardStatsApiView
)

router = DefaultRouter()
router.register(r'reports', AnalyticsReportViewSet, basename='analytics-reports')
router.register(r'productivity', ProductivityMetricsViewSet, basename='productivity-metrics')
router.register(r'time-tracking', TimeTrackingViewSet, basename='time-tracking')
router.register(r'indicators', PerformanceIndicatorViewSet, basename='performance-indicators')
router.register(r'widgets', DashboardWidgetViewSet, basename='dashboard-widgets')

urlpatterns = [
    path('', AnalyticsPageView.as_view(), name='analytics'),  # HTML page
    path('api/', include(router.urls)),  # REST API
    path('api/stats/', DashboardStatsApiView.as_view(), name='analytics-stats'),  # Dashboard stats
]