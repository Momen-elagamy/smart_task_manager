from django.urls import path
from .views import GoogleCalendarView, SlackMessageView

urlpatterns = [
    path('google-calendar/', GoogleCalendarView.as_view(), name='google-calendar'),
    path('slack-message/', SlackMessageView.as_view(), name='slack-message'),
]
