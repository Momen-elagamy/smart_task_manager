from datetime import datetime, timedelta
from tasks.models import Task
from projects.models import Project

def get_user_stats(user):
    tasks = Task.objects.filter(project__owner=user)
    total = tasks.count()
    done = tasks.filter(status="done").count()
    overdue = tasks.filter(status="todo", due_date__lt=datetime.now()).count()
    
    completion_rate = round((done / total) * 100, 2) if total > 0 else 0

    return {
        "total_tasks": total,
        "completed_tasks": done,
        "overdue_tasks": overdue,
        "completion_rate": completion_rate
    }

def get_project_stats(project):
    tasks = Task.objects.filter(project=project)
    total = tasks.count()
    done = tasks.filter(status="done").count()
    overdue = tasks.filter(status="todo", due_date__lt=datetime.now()).count()
    rate = round((done / total) * 100, 2) if total > 0 else 0

    return {
        "project_name": project.name,
        "total_tasks": total,
        "completed_tasks": done,
        "overdue_tasks": overdue,
        "completion_rate": rate
    }

def get_overall_stats():
    projects = Project.objects.all()
    summary = [get_project_stats(p) for p in projects]
    avg_completion = 0
    if summary:
        avg_completion = round(sum(s["completion_rate"] for s in summary) / len(summary), 2)
    return {
        "projects_count": projects.count(),
        "avg_completion_rate": avg_completion,
        "projects": summary
    }
