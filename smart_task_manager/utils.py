"""
Custom exception handler and utility functions for Smart Task Manager.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    
    Args:
        exc: The exception instance
        context: The context of the request
    
    Returns:
        Response: Formatted error response
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize error response format
        custom_response_data = {
            'success': False,
            'error': {
                'message': str(exc),
                'type': exc.__class__.__name__,
                'status_code': response.status_code,
            }
        }
        
        # Add detail if available
        if hasattr(exc, 'detail'):
            custom_response_data['error']['detail'] = exc.detail
        
        response.data = custom_response_data
        
        # Log error
        logger.error(
            f"API Error: {exc.__class__.__name__} - {str(exc)}",
            extra={
                'status_code': response.status_code,
                'path': context['request'].path,
                'method': context['request'].method,
            }
        )
    else:
        # Handle unexpected errors
        logger.exception(f"Unhandled exception: {str(exc)}")
        response = Response(
            {
                'success': False,
                'error': {
                    'message': 'An unexpected error occurred.',
                    'type': 'InternalServerError',
                    'status_code': 500,
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response


def validate_file_size(file, max_size_mb=5):
    """
    Validate uploaded file size.
    
    Args:
        file: The uploaded file object
        max_size_mb: Maximum file size in megabytes
    
    Returns:
        bool: True if valid
    
    Raises:
        ValidationError: If file is too large
    """
    from django.core.exceptions import ValidationError
    
    max_size_bytes = max_size_mb * 1024 * 1024
    if file.size > max_size_bytes:
        raise ValidationError(
            f'File size exceeds maximum allowed size of {max_size_mb}MB'
        )
    return True


def validate_file_extension(file, allowed_extensions):
    """
    Validate file extension.
    
    Args:
        file: The uploaded file object
        allowed_extensions: List of allowed extensions
    
    Returns:
        bool: True if valid
    
    Raises:
        ValidationError: If extension not allowed
    """
    from django.core.exceptions import ValidationError
    import os
    
    ext = os.path.splitext(file.name)[1].lower().replace('.', '')
    if ext not in allowed_extensions:
        raise ValidationError(
            f'File extension .{ext} is not allowed. Allowed: {", ".join(allowed_extensions)}'
        )
    return True
