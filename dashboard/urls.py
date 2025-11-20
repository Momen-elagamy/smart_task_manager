from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardViewSet, DashboardWidgetViewSet, DashboardFilterViewSet

router = DefaultRouter()
router.register(r'dashboards', DashboardViewSet, basename='dashboards')
router.register(r'widgets', DashboardWidgetViewSet, basename='dashboard-widgets')
router.register(r'filters', DashboardFilterViewSet, basename='dashboard-filters')

urlpatterns = [
    path('', include(router.urls)),
]









