from celery import shared_task
from celery.schedules import crontab
from .models import Task
from datetime import date, timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

CELERY_BEAT_SCHEDULE = {
    'generate-recurring-tasks-everyday': {
        'task': 'tasks.tasks.generate_recurring_tasks',
        'schedule': crontab(hour=0, minute=0),  # كل يوم منتصف الليل
    },
    'check-due-date-reminders': {
        'task': 'tasks.tasks.check_due_date_reminders',
        'schedule': crontab(hour=9, minute=0),  # كل يوم 9 صباحاً
    },
    'send-overdue-reminders': {
        'task': 'tasks.tasks.send_overdue_reminders',
        'schedule': crontab(hour=10, minute=0),  # كل يوم 10 صباحاً
    },
}

@shared_task
def generate_recurring_tasks():
    today = date.today()
    tasks_to_recreate = Task.objects.filter(recurrence__in=['daily', 'weekly', 'monthly'], due_date__lte=today)
    created_count = 0
    for task in tasks_to_recreate:
        if task.create_next_recurrence():
            created_count += 1
    return f"{created_count} recurring tasks generated."


@shared_task
def check_due_date_reminders():
    """
    Check for tasks due soon and send reminders.
    Run daily to check tasks due in 1 day, 3 days, or today.
    """
    now = timezone.now().date()
    
    # Tasks due today
    tasks_due_today = Task.objects.filter(
        due_date=now,
        status__in=['todo', 'in_progress'],
        assigned_to__isnull=False
    ).select_related('assigned_to', 'project')
    
    # Tasks due in 1 day
    tasks_due_1day = Task.objects.filter(
        due_date=now + timedelta(days=1),
        status__in=['todo', 'in_progress'],
        assigned_to__isnull=False
    ).select_related('assigned_to', 'project')
    
    # Tasks due in 3 days
    tasks_due_3days = Task.objects.filter(
        due_date=now + timedelta(days=3),
        status__in=['todo', 'in_progress'],
        assigned_to__isnull=False
    ).select_related('assigned_to', 'project')
    
    sent_count = 0
    
    # Send reminders for tasks due today (urgent)
    for task in tasks_due_today:
        if send_task_reminder(task, 'today'):
            sent_count += 1
    
    # Send reminders for tasks due in 1 day
    for task in tasks_due_1day:
        if send_task_reminder(task, '1 day'):
            sent_count += 1
    
    # Send reminders for tasks due in 3 days
    for task in tasks_due_3days:
        if send_task_reminder(task, '3 days'):
            sent_count += 1
    
    logger.info(f"Sent {sent_count} due date reminder emails")
    return f"{sent_count} due date reminders sent"


def send_task_reminder(task, timeframe):
    """
    Send email reminder for a specific task.
    
    Args:
        task: Task instance
        timeframe: String like 'today', '1 day', '3 days'
    
    Returns:
        bool: True if email sent successfully
    """
    try:
        subject = f"⏰ Task Due {timeframe.title()}: {task.title}"
        
        message = f"""
Hello {task.assigned_to.get_full_name() or task.assigned_to.email},

This is a reminder that the following task is due {timeframe}:

Task: {task.title}
Project: {task.project.name}
Due Date: {task.due_date.strftime('%B %d, %Y')}
Priority: {task.get_priority_display()}
Status: {task.get_status_display()}

Description:
{task.description or 'No description provided'}

Please make sure to complete this task on time.

---
Smart Task Manager
This is an automated message, please do not reply.
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[task.assigned_to.email],
            fail_silently=False,
        )
        
        logger.info(f"Sent reminder to {task.assigned_to.email} for task {task.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send reminder for task {task.id}: {str(e)}")
        return False


@shared_task
def send_overdue_reminders():
    """
    Send reminders for overdue tasks.
    Run daily to notify about tasks past their due date.
    """
    now = timezone.now().date()
    
    overdue_tasks = Task.objects.filter(
        due_date__lt=now,
        status__in=['todo', 'in_progress'],
        assigned_to__isnull=False
    ).select_related('assigned_to', 'project')
    
    sent_count = 0
    
    for task in overdue_tasks:
        days_overdue = (now - task.due_date).days
        
        try:
            subject = f"🚨 OVERDUE: {task.title} ({days_overdue} days)"
            
            message = f"""
Hello {task.assigned_to.get_full_name() or task.assigned_to.email},

This task is now OVERDUE by {days_overdue} day(s):

Task: {task.title}
Project: {task.project.name}
Was Due: {task.due_date.strftime('%B %d, %Y')}
Priority: {task.get_priority_display()}
Status: {task.get_status_display()}

Please complete this task as soon as possible or update its status.

---
Smart Task Manager
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[task.assigned_to.email],
                fail_silently=False,
            )
            
            sent_count += 1
            logger.info(f"Sent overdue reminder to {task.assigned_to.email} for task {task.id}")
            
        except Exception as e:
            logger.error(f"Failed to send overdue reminder for task {task.id}: {str(e)}")
    
    logger.info(f"Sent {sent_count} overdue reminder emails")
    return f"{sent_count} overdue reminders sent"
