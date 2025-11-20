from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required(login_url='login')
def dashboard_page(request):
    """Renders the main dashboard page."""
    return render(request, 'dashboard.html')


@login_required(login_url='login')
def tasks_page(request):
    """Renders the tasks page."""
    return render(request, 'tasks.html')


@login_required(login_url='login')
def task_detail_page(request):
    """Renders the task detail page."""
    return render(request, 'task_detail.html')


@login_required(login_url='login')
def projects_page(request):
    """Renders the projects page."""
    return render(request, 'projects.html')


@login_required(login_url='login')
def chat_page(request):
    """Renders the chat page."""
    return render(request, 'chat.html')


@login_required(login_url='login')
def team_page(request):
    """Renders the team page."""
    return render(request, 'team.html')


@login_required(login_url='login')
def analytics_page(request):
    """Renders the analytics page."""
    return render(request, 'analytics.html')


@login_required(login_url='login')
def settings_page(request):
    """Renders the settings page."""
    return render(request, 'settings.html')


def forgot_password_page(request):
    """Renders the forgot password page - public page."""
    return render(request, 'forgot_password.html')


@login_required(login_url='login')
def security_settings_page(request):
    """Renders the security settings page."""
    return render(request, 'security_settings.html')


@login_required(login_url='login')
def direct_messages_page(request, room_id):
    """Render a simple Direct Messages page for a given room."""
    from chat.models import ChatRoom
    from django.http import Http404
    
    try:
        room = ChatRoom.objects.get(id=room_id)
        if request.user not in room.members.all():
            return redirect('dashboard')
    except ChatRoom.DoesNotExist:
        return redirect('dashboard')
    
    return render(request, 'direct_chat.html', { 'room_id': room_id })