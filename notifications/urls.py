from django.urls import path
from .views import (
    NotificationListView,
    NotificationMarkReadView,
    RegisterFCMTokenView,
    MarkAllReadView,
    notification_count,
    notifications_page_view,
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notifications-list'),  # JSON API list
    path('page/', notifications_page_view, name='notifications-page'),    # HTML page
    path('count/', notification_count, name='notification-count'),
    path('mark-all-read/', MarkAllReadView.as_view(), name='mark-all-read'),
    path('<uuid:pk>/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('register-fcm-token/', RegisterFCMTokenView.as_view(), name='register-fcm-token'),
]
