from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, ProjectListCreateView, ProjectDetailView

# Create router for ViewSet
router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Legacy URLs for backward compatibility
    path('legacy/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('legacy/<uuid:pk>/', ProjectDetailView.as_view(), name='project-detail'),
]
