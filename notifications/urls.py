from django.urls import path
from .views import (
    NotificationListView, 
    NotificationMarkReadView, 
    RegisterFCMTokenView,
    mark_all_read,
    notification_count
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notifications-list'),
    path('count/', notification_count, name='notification-count'),
    path('mark-all-read/', mark_all_read, name='mark-all-read'),
    path('<uuid:pk>/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('register-fcm-token/', RegisterFCMTokenView.as_view(), name='register-fcm-token'),
]
