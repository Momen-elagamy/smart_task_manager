from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome_view, name='welcome'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('chat/', views.chat_view, name='chat'),
    path('profile/', views.profile_view, name='profile'),
    path('api/stats/', views.stats_api, name='stats_api'),
]








