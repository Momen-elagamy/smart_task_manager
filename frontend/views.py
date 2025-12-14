from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required

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

@login_required
def team_view(request):
    """Render team page (list of users)"""
    return render(request, 'users/team_list.html')

@login_required
def settings_view(request):
    """Render settings page"""
    return render(request, 'settings.html')

def api_explorer_view(request):
    """Simple page to interact with all API endpoints"""
    return render(request, 'frontend/api_explorer.html')

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


@login_required
def logout_view(request):
    """Log out the user and redirect to welcome page"""
    logout(request)
    return redirect('welcome')








