from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json

def register_view(request):
    """Render registration page"""
    return render(request, 'register.html')

def login_view(request):
    """Render login page"""
    return render(request, 'login.html')

def dashboard_view(request):
    """Render dashboard page"""
    return render(request, 'dashboard.html')

def chat_view(request):
    """Render AI chat page"""
    return render(request, 'chat.html')

def welcome_view(request):
    """Render welcome page"""
    return render(request, 'welcome.html')

@login_required
def profile_view(request):
    """Render user profile page"""
    return render(request, 'profile.html')

def stats_api(request):
    """API endpoint for dashboard stats"""
    if request.method == 'GET':
        # Mock data - in production, this would come from your database
        stats = {
            'users': 1250,
            'projects': 45,
            'tasks': 320,
            'time_saved': 150
        }
        return JsonResponse(stats)
    return JsonResponse({'error': 'Method not allowed'}, status=405)








