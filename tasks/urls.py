from django.urls import include
from rest_framework.routers import DefaultRouter
from . import views

# API router (export API endpoints only from this module)
router = DefaultRouter()
router.register(r'tasks', views.TaskViewSet, basename='api-tasks')
router.register(r'comments', views.CommentViewSet, basename='api-comments')
router.register(r'attachments', views.AttachmentViewSet, basename='api-attachments')
router.register(r'tags', views.TagViewSet, basename='api-tags')

# Important: Do NOT include frontend views here to avoid mixing HTML under /api/
urlpatterns = router.urls
