"""
Role-Based Access Control (RBAC) permissions for Django REST Framework.

This module provides:
1. RolePermission class for DRF viewsets
2. @roles_required decorator for Django function views
3. Utility functions for role checking
"""

from rest_framework import permissions
from functools import wraps
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied


class RolePermission(permissions.BasePermission):
    """
    DRF Permission class that checks if user has required roles.
    
    Usage in ViewSets:
    class MyViewSet(viewsets.ModelViewSet):
        permission_classes = [RolePermission]
        allowed_roles = ['admin', 'manager']  # Define allowed roles
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to access the view.
        """
        # Allow unauthenticated users to pass through (handled by IsAuthenticated)
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get allowed roles from view
        allowed_roles = getattr(view, 'allowed_roles', [])
        
        # If no roles specified, deny access
        if not allowed_roles:
            return False
        
        # Check if user has profile and required role
        if hasattr(request.user, 'profile'):
            return request.user.profile.has_role(*allowed_roles)
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to access a specific object.
        """
        # First check basic permission
        if not self.has_permission(request, view):
            return False
        
        # Get object-level roles if defined
        object_roles = getattr(view, 'object_allowed_roles', [])
        
        # If no object roles specified, use view roles
        if not object_roles:
            object_roles = getattr(view, 'allowed_roles', [])
        
        # Check if user has required role for this object
        if hasattr(request.user, 'profile'):
            return request.user.profile.has_role(*object_roles)
        
        return False


def roles_required(*roles):
    """
    Decorator for Django function views to require specific roles.
    
    Usage:
    @roles_required('admin', 'manager')
    def my_view(request):
        # View logic here
        pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse(
                    {'error': 'Authentication required'}, 
                    status=401
                )
            
            # Check if user has profile
            if not hasattr(request.user, 'profile'):
                return JsonResponse(
                    {'error': 'User profile not found'}, 
                    status=403
                )
            
            # Check if user has required role
            if not request.user.profile.has_role(*roles):
                return JsonResponse(
                    {'error': f'Access denied. Required roles: {", ".join(roles)}'}, 
                    status=403
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def has_role(user, *roles):
    """
    Utility function to check if a user has any of the specified roles.
    
    Args:
        user: Django User instance
        *roles: Role names to check
    
    Returns:
        bool: True if user has any of the roles, False otherwise
    """
    if not user or not user.is_authenticated:
        return False
    
    if not hasattr(user, 'profile'):
        return False
    
    return user.profile.has_role(*roles)


def is_admin(user):
    """Check if user is an admin."""
    return has_role(user, 'admin')


def is_manager(user):
    """Check if user is a manager or admin."""
    return has_role(user, 'admin', 'manager')


def is_developer(user):
    """Check if user is a developer, manager, or admin."""
    return has_role(user, 'admin', 'manager', 'developer')


def is_client(user):
    """Check if user is a client."""
    return has_role(user, 'client')


def get_user_role(user):
    """
    Get the role of a user.
    
    Args:
        user: Django User instance
    
    Returns:
        str: User's role or None if not found
    """
    if not user or not user.is_authenticated:
        return None
    
    if not hasattr(user, 'profile'):
        return None
    
    return user.profile.role


def can_access_object(user, obj, owner_field='owner'):
    """
    Check if user can access an object based on ownership or role.
    
    Args:
        user: Django User instance
        obj: Object to check access for
        owner_field: Field name that contains the owner
    
    Returns:
        bool: True if user can access the object
    """
    if not user or not user.is_authenticated:
        return False
    
    # Admins can access everything
    if is_admin(user):
        return True
    
    # Check if user is the owner
    if hasattr(obj, owner_field):
        owner = getattr(obj, owner_field)
        if owner == user:
            return True
    
    # Managers can access objects in their scope
    if is_manager(user):
        return True
    
    return False

