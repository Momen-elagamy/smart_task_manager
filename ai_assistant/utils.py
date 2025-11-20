from tasks.models import Task
from datetime import datetime, timedelta

def analyze_productivity(user):
    tasks = Task.objects.filter(project__owner=user)
    completed = tasks.filter(status="done").count()
    total = tasks.count()

    productivity = round((completed / total) * 100, 2) if total > 0 else 0
    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "productivity": productivity,
    }

def suggest_tasks(user):
    tasks = Task.objects.filter(project__owner=user)
    if not tasks.exists():
        return ["Start by creating your first task today! 🚀"]
    
    # Logic: إذا كان بيعمل على project طويل المدى، نقترح متابعة progress
    suggestions = []
    upcoming = tasks.filter(status="in_progress", due_date__gte=datetime.now())
    if upcoming.exists():
        suggestions.append("You have ongoing tasks — focus on completing them first ✅")

    overdue = tasks.filter(status="todo", due_date__lt=datetime.now())
    if overdue.exists():
        suggestions.append("You have overdue tasks — try to finish them soon ⚠️")

    return suggestions or ["Everything looks good today! 😎"]
