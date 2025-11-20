from django.http import JsonResponse
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from tasks.models import Task
from projects.models import Project
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def global_search(request):
    """
    Global search across tasks, projects, and users.
    Query params:
    - q: search query
    - type: filter by type (task, project, user, all)
    - limit: max results per type (default 5)
    """
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')
    limit = int(request.GET.get('limit', 5))
    
    if not query or len(query) < 2:
        return JsonResponse({'results': [], 'message': 'Query too short'})
    
    results = {
        'tasks': [],
        'projects': [],
        'users': [],
        'total': 0
    }
    
    user = request.user
    profile = getattr(user, 'profile', None)
    
    # Search Tasks
    if search_type in ['all', 'task']:
        tasks_qs = Task.objects.select_related('assigned_to', 'project').filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )
        
        # Apply RBAC filtering
        if not (profile and hasattr(profile, 'has_role') and profile.has_role('admin', 'manager')):
            if profile and profile.has_role('developer'):
                tasks_qs = tasks_qs.filter(Q(assigned_to=user) | Q(project__owner=user))
            else:
                tasks_qs = tasks_qs.filter(project__owner=user)
        
        for task in tasks_qs[:limit]:
            results['tasks'].append({
                'id': task.id,
                'title': task.title,
                'description': task.description[:100] if task.description else '',
                'status': task.status,
                'project': task.project.name if task.project else None,
                'assigned_to': task.assigned_to.email if task.assigned_to else None,
                'url': f'/tasks/?task={task.id}'
            })
    
    # Search Projects
    if search_type in ['all', 'project']:
        projects_qs = Project.objects.select_related('owner').filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
        
        # Apply RBAC filtering
        if not (profile and hasattr(profile, 'has_role') and profile.has_role('admin', 'manager')):
            projects_qs = projects_qs.filter(Q(owner=user) | Q(members=user))
        
        for project in projects_qs.distinct()[:limit]:
            results['projects'].append({
                'id': project.id,
                'name': project.name,
                'description': project.description[:100] if project.description else '',
                'owner': project.owner.email if project.owner else None,
                'url': f'/projects/{project.id}/'
            })
    
    # Search Users (only for admins/managers)
    if search_type in ['all', 'user'] and profile and profile.has_role('admin', 'manager'):
        users_qs = User.objects.filter(
            Q(email__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        )
        
        for u in users_qs[:limit]:
            results['users'].append({
                'id': u.id,
                'email': u.email,
                'name': f"{u.first_name} {u.last_name}".strip() or u.email,
                'role': getattr(getattr(u, 'profile', None), 'role', 'member'),
                'url': f'/profile/{u.email}/'
            })
    
    results['total'] = len(results['tasks']) + len(results['projects']) + len(results['users'])
    
    return JsonResponse(results)
