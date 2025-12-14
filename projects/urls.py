from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, ProjectListCreateView, ProjectDetailView
from .views import ProjectsPageView

# Create router for ViewSet
router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')

urlpatterns = [
    # Original router-based URLs
        path('', ProjectsPageView.as_view(), name='projects'),  # HTML page
        path('api/', include(router.urls)),  # REST API under /projects/api/
    # Legacy URLs
    path('legacy/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('legacy/<uuid:pk>/', ProjectDetailView.as_view(), name='project-detail'),
]
