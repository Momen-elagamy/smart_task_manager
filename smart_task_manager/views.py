from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.cache import cache
from django.contrib.auth import get_user_model
from projects.models import Project
from tasks.models import Task
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.authentication import JWTAuthentication
from datetime import timedelta

User = get_user_model()

def welcome_page(request):
    """صفحة الترحيب الرئيسية"""
    return render(request, 'welcome.html')

def stats_api(request):
    """User-scoped dashboard stats for tasks.

    Returns keys expected by the frontend:
    - total_tasks
    - pending_tasks (maps to Task.status in ['todo'])
    - in_progress_tasks (Task.status == 'in_progress')
    - completed_tasks (Task.status in ['done', 'completed'])
    """
    try:
        user = request.user

        # Build queryset based on role (mirror TaskViewSet logic roughly)
        qs = Task.objects.all()

        try:
            profile = getattr(user, 'profile', None)
        except Exception:
            profile = None

        if not user.is_authenticated:
            # Try to authenticate via JWT (Authorization: Bearer ...)
            try:
                jwt_auth = JWTAuthentication()
                auth_result = jwt_auth.authenticate(request)
                if auth_result is not None:
                    user, _token = auth_result
                    profile = getattr(user, 'profile', None)
                else:
                    return JsonResponse({
                        'total_tasks': 0,
                        'pending_tasks': 0,
                        'in_progress_tasks': 0,
                        'completed_tasks': 0,
                    })
            except Exception:
                return JsonResponse({
                    'total_tasks': 0,
                    'pending_tasks': 0,
                    'in_progress_tasks': 0,
                    'completed_tasks': 0,
                })
        elif profile and hasattr(profile, 'has_role') and profile.has_role('admin', 'manager'):
            # Admins and managers: all tasks
            pass
        elif profile and profile.has_role('developer'):
            qs = Task.objects.filter(Q(assigned_to=user) | Q(project__owner=user)).distinct()
        else:
            # Clients or others: tasks in their projects
            qs = Task.objects.filter(project__owner=user)

        # Compute counts with status mapping
        total_tasks = qs.count()
        pending_tasks = qs.filter(status__in=['todo', 'pending']).count()
        in_progress_tasks = qs.filter(status='in_progress').count()
        completed_tasks = qs.filter(status__in=['done', 'completed']).count()

        return JsonResponse({
            'total_tasks': total_tasks,
            'pending_tasks': pending_tasks,
            'in_progress_tasks': in_progress_tasks,
            'completed_tasks': completed_tasks,
        })
    except Exception:
        # Safe fallback
        return JsonResponse({
            'total_tasks': 0,
            'pending_tasks': 0,
            'in_progress_tasks': 0,
            'completed_tasks': 0,
        })

def frontend_redirect(request):
    """إعادة توجيه إلى الواجهة الأمامية"""
    return render(request, 'frontend_redirect.html')

def register_view(request):
    """صفحة التسجيل"""
    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'register.html')

def login_view(request):
    """صفحة الدخول"""
    # Redirect if already logged in
    if request.user.is_authenticated:
        # If there's a 'next' parameter, go there
        next_url = request.GET.get('next', 'dashboard')
        return redirect(next_url)
    return render(request, 'login.html')

def logout_view(request):
    """صفحة تسجيل الخروج"""
    # Clear Django session
    logout(request)
    
    # Create response to redirect to login
    response = redirect('login')
    
    # Very aggressive cookie deletion - try multiple methods
    cookie_names = [
        'access_token',
        'refresh_token', 
        'sessionid',
        'csrftoken',
        'remember_me_token',
        'userEmail',
        'rememberMe'
    ]
    
    # Delete using Django's delete_cookie method with different paths
    for cookie_name in cookie_names:
        response.delete_cookie(cookie_name, path='/', domain=None)
        response.delete_cookie(cookie_name, path='/api/', domain=None)
        response.delete_cookie(cookie_name, path='', domain=None)
    
    # Also set Set-Cookie headers directly to ensure browser deletion
    for cookie_name in cookie_names:
        response['Set-Cookie'] = f'{cookie_name}=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Max-Age=0'
    
    # Clear session data completely
    if hasattr(request, 'session'):
        request.session.flush()
    
    return response

@login_required(login_url='login')
def profile_view(request, username):
    """صفحة الملف الشخصي"""
    # استخدم select_related لجلب بيانات المستخدم والملف الشخصي في استعلام واحد
    # The CustomUser model uses 'email' as the USERNAME_FIELD.
    # Assuming 'username' in the URL is the user's email.
    user = get_object_or_404(User.objects.select_related('profile'), email=username)

    # استخدم prefetch_related لجلب المشاريع والمهام في استعلامات منفصلة ومُحسّنة
    projects = user.projects_owned.prefetch_related('members').order_by('-created_at')[:5]
    tasks = Task.objects.filter(assigned_to=user).select_related('project').order_by('-due_date')[:5]
    
    context = {
        'profile_user': user,
        'projects': projects,
        'tasks': tasks,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='login')
def project_detail_view(request, project_id):
    """صفحة تفاصيل المشروع"""
    # استخدم prefetch_related لجلب كل المهام والأعضاء في استعلامات قليلة
    project = get_object_or_404(
        Project.objects.prefetch_related('task_set', 'members'),
        id=project_id
    )
    return render(request, 'project_detail.html', {'project': project})

@login_required(login_url='login')
def team_members_api(request):
    """Return team members with basic metrics.

    Fields per member:
    - id, first_name, last_name, email, username
    - role (from profile if available)
    - status (heuristic: 'online' if is_active else 'offline')
    - task_count
    - completion_rate (completed/assigned * 100)
    """
    try:
        user = request.user

        if not user.is_authenticated:
            try:
                jwt_auth = JWTAuthentication()
                auth_result = jwt_auth.authenticate(request)
                if auth_result is not None:
                    user, _token = auth_result
            except Exception:
                pass

        # For now, list all users. In a multi-tenant setup, scope this appropriately.
        users_qs = User.objects.all().select_related('profile')

        members = []
        for u in users_qs:
            tasks_qs = Task.objects.filter(assigned_to=u)
            total = tasks_qs.count()
            done = tasks_qs.filter(status__in=['done', 'completed']).count()
            completion_rate = int(round((done / total) * 100)) if total else 0
            role = None
            profile = getattr(u, 'profile', None)
            if profile is not None:
                role = getattr(profile, 'role', None)

            members.append({
                'id': u.id,
                'first_name': u.first_name or '',
                'last_name': u.last_name or '',
                'email': u.email,
                'username': getattr(u, 'username', None) or u.email,
                'role': role or 'member',
                'department': getattr(profile, 'department', None) if profile else None,
                'status': 'online' if u.is_active else 'offline',
                'task_count': total,
                'completion_rate': completion_rate,
            })

        return JsonResponse({'results': members})
    except Exception:
        return JsonResponse({'results': []})

@login_required(login_url='login')
def recent_activity_api(request):
    """Return recent activity from tasks and projects.
    
    Returns a list of activity items with:
    - type: 'task_created', 'task_completed', 'task_updated', 'project_created'
    - user: email of user who performed action
    - title: task or project name
    - description: formatted activity description
    - timestamp: ISO formatted datetime
    - time_ago: human-readable time string
    """
    try:
        from datetime import datetime
        
        activities = []
        
        # Get recent tasks (created, completed, updated)
        recent_tasks = Task.objects.select_related('assigned_to', 'project', 'created_by').order_by('-created_at')[:10]
        
        for task in recent_tasks:
            now = timezone.now()
            time_diff = now - task.created_at
            
            # Calculate human-readable time
            if time_diff.days == 0:
                if time_diff.seconds < 3600:
                    time_ago = f"{time_diff.seconds // 60} minutes ago"
                elif time_diff.seconds < 7200:
                    time_ago = "1 hour ago"
                else:
                    time_ago = f"{time_diff.seconds // 3600} hours ago"
            elif time_diff.days == 1:
                time_ago = "Yesterday"
            elif time_diff.days < 7:
                time_ago = f"{time_diff.days} days ago"
            else:
                time_ago = task.created_at.strftime("%b %d, %Y")
            
            user_email = task.assigned_to.email if task.assigned_to else (task.created_by.email if task.created_by else "Unknown")
            user_name = user_email.split('@')[0].title()
            
            # Determine activity type
            if task.status in ['done', 'completed']:
                activity_type = 'task_completed'
                icon = 'check-circle'
                description = f"{user_name} completed task <strong>{task.title}</strong>"
            elif task.status == 'in_progress':
                activity_type = 'task_updated'
                icon = 'sync'
                description = f"{user_name} is working on <strong>{task.title}</strong>"
            else:
                activity_type = 'task_created'
                icon = 'plus-circle'
                description = f"{user_name} created task <strong>{task.title}</strong>"
            
            activities.append({
                'type': activity_type,
                'icon': icon,
                'user': user_email,
                'user_name': user_name,
                'title': task.title,
                'description': description,
                'timestamp': task.created_at.isoformat(),
                'time_ago': time_ago,
            })
        
        # Get recent projects
        recent_projects = Project.objects.select_related('owner').order_by('-created_at')[:5]
        
        for project in recent_projects:
            now = timezone.now()
            time_diff = now - project.created_at
            
            if time_diff.days == 0:
                if time_diff.seconds < 3600:
                    time_ago = f"{time_diff.seconds // 60} minutes ago"
                elif time_diff.seconds < 7200:
                    time_ago = "1 hour ago"
                else:
                    time_ago = f"{time_diff.seconds // 3600} hours ago"
            elif time_diff.days == 1:
                time_ago = "Yesterday"
            elif time_diff.days < 7:
                time_ago = f"{time_diff.days} days ago"
            else:
                time_ago = project.created_at.strftime("%b %d, %Y")
            
            user_email = project.owner.email if project.owner else "Unknown"
            user_name = user_email.split('@')[0].title()
            
            activities.append({
                'type': 'project_created',
                'icon': 'folder-plus',
                'user': user_email,
                'user_name': user_name,
                'title': project.name,
                'description': f"{user_name} created project <strong>{project.name}</strong>",
                'timestamp': project.created_at.isoformat(),
                'time_ago': time_ago,
            })
        
        # Sort all activities by timestamp (most recent first)
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Return top 10
        return JsonResponse({'results': activities[:10]})
        
    except Exception as e:
        return JsonResponse({'results': [], 'error': str(e)})
