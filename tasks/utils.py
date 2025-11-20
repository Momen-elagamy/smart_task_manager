"""
Utility functions for task management, including mention handling.
"""

import re
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()


def handle_mentions_in_comment(comment_content, task, author):
    """
    Detect mentions in comment content and create notifications for mentioned users.
    
    Args:
        comment_content (str): The content of the comment
        task: Task instance
        author: User who wrote the comment
        
    Returns:
        list: List of mentioned users
    """
    # Regex pattern to find mentions: @username (including @ in email)
    mention_pattern = r'@([A-Za-z0-9_\.@]+)'
    mentions = re.findall(mention_pattern, comment_content)
    
    mentioned_users = []
    
    for username in mentions:
        try:
            # Try to find user by email (assuming username is email)
            user = User.objects.get(email=username)
            
            # Don't notify the author of the comment
            if user != author:
                # Create notification for mentioned user
                message = f"You were mentioned in a comment on task '{task.title}' by {author.email}"
                
                Notification.objects.create(
                    user=user,
                    message=message,
                    task=task,
                    notification_type='web'
                )
                
                mentioned_users.append(user)
                
        except User.DoesNotExist:
            # User not found, skip this mention
            continue
    
    return mentioned_users


def extract_mentions_from_text(text):
    """
    Extract all mentions from text using regex.
    
    Args:
        text (str): Text to search for mentions
        
    Returns:
        list: List of mentioned usernames
    """
    mention_pattern = r'@([A-Za-z0-9_\.]+)'
    return re.findall(mention_pattern, text)


def get_mentioned_users(text):
    """
    Get User objects for all mentioned usernames in text.
    
    Args:
        text (str): Text to search for mentions
        
    Returns:
        list: List of User objects that were mentioned
    """
    mentions = extract_mentions_from_text(text)
    users = []
    
    for username in mentions:
        try:
            user = User.objects.get(email=username)
            users.append(user)
        except User.DoesNotExist:
            continue
    
    return users


def create_task_notification(user, task, message, notification_type='web'):
    """
    Create a notification for a user about a task.
    
    Args:
        user: User to notify
        task: Task instance
        message (str): Notification message
        notification_type (str): Type of notification
        
    Returns:
        Notification: Created notification instance
    """
    return Notification.objects.create(
        user=user,
        message=message,
        task=task,
        notification_type=notification_type
    )


def notify_task_assignees(task, message, exclude_user=None):
    """
    Notify all users assigned to a task.
    
    Args:
        task: Task instance
        message (str): Notification message
        exclude_user: User to exclude from notifications
        
    Returns:
        list: List of created notifications
    """
    notifications = []
    
    # Notify the task assignee if they exist
    if task.assigned_to and task.assigned_to != exclude_user:
        notification = create_task_notification(
            task.assigned_to, 
            task, 
            message
        )
        notifications.append(notification)
    
    # Notify project owner if they're not the assignee
    if (task.project.owner and 
        task.project.owner != task.assigned_to and 
        task.project.owner != exclude_user):
        notification = create_task_notification(
            task.project.owner, 
            task, 
            message
        )
        notifications.append(notification)
    
    return notifications
