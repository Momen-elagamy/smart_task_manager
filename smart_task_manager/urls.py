"""
URL configuration for smart_task_manager project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from users.views import (
    UserRegisterApiView,
    UserLoginApiView,
    TeamMembersApiView,
    UserProfileApiView,
    UserLogoutApiView,
    TeamPageView,
    InviteApiView,
)
from core.views import search_api, recent_activity_api
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from django.conf import settings
from django.conf.urls.static import static
from tasks.views import CommentViewSet, AttachmentViewSet, TaskViewSet
from projects.views import ProjectViewSet
from rest_framework.routers import DefaultRouter

# Create router for conventional /api/tasks/ and /api/projects/ endpoints
api_router = DefaultRouter()
api_router.register(r'tasks', TaskViewSet, basename='api-tasks')
api_router.register(r'projects', ProjectViewSet, basename='api-projects')
api_router.register(r'comments', CommentViewSet, basename='api-comments-alt')
api_router.register(r'attachments', AttachmentViewSet, basename='api-attachments-alt')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('frontend.urls')),
    path('users/', include('users.urls')),
    path('team/', TeamPageView.as_view(), name='team'),  # Team page
    path('api/users/register/', UserRegisterApiView.as_view(), name='api-user-register'),
    path('api/users/login/', UserLoginApiView.as_view(), name='api-user-login'),
    path('api/users/team/', TeamMembersApiView.as_view(), name='api-users-team'),
    path('api/team/members/', TeamMembersApiView.as_view(), name='api-team-members'),
    path('api/users/profile/', UserProfileApiView.as_view(), name='api-user-profile'),
    path('api/users/logout/', UserLogoutApiView.as_view(), name='api-user-logout'),
    path('api/users/invite/', InviteApiView.as_view(), name='api-user-invite'),
    path('api/users/token/', TokenObtainPairView.as_view(), name='api-token-obtain'),
    path('api/users/token/refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),
    path('api/users/token/verify/', TokenVerifyView.as_view(), name='api-token-verify'),
    # Conventional JWT aliases for tests and integrations
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # Conventional /api/ endpoints (tasks, projects, comments, attachments)
    path('api/', include(api_router.urls)),
    path('api/search/', search_api, name='api-search'),
    path('api/activity/recent/', recent_activity_api, name='api-activity-recent'),
    path('api/dashboard/', include('dashboard.urls')),  # API dashboard endpoints
    path('projects/', include('projects.urls')),
    path('tasks/', include('tasks.urls')),
    path('analytics/', include('analytics.urls')),
    path('notifications/', include('notifications.urls')),
    path('chat/', include('chat.urls')),
    path('payments/', include('payments.urls')),
    path('dashboard/', include('dashboard.urls')),  # HTML dashboard views
    path('ai/', include('ai_assistant.urls')),
    # Fix LOGIN_URL mismatch: some redirects go to /accounts/login/ but only /login/ exists inside frontend/users.
    # Provide alias redirect so LoginRequiredMixin doesn't 404.
    path('accounts/login/', RedirectView.as_view(pattern_name='login', permanent=False)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
