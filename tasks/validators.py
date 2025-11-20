"""
File validation utilities for task attachments.
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_file_size(file_obj):
    """
    Validate that file size is within allowed limits.
    
    Args:
        file_obj: Django UploadedFile object
        
    Raises:
        ValidationError: If file size exceeds limit
    """
    from .models import Attachment
    
    if file_obj.size > Attachment.MAX_FILE_SIZE:
        max_size_mb = Attachment.MAX_FILE_SIZE / (1024 * 1024)
        raise ValidationError(
            _('File size cannot exceed %(max_size)s MB. Current size: %(current_size)s MB.'),
            params={
                'max_size': max_size_mb,
                'current_size': round(file_obj.size / (1024 * 1024), 2)
            }
        )


def validate_content_type(file_obj):
    """
    Validate that file type is allowed.
    
    Args:
        file_obj: Django UploadedFile object
        
    Raises:
        ValidationError: If file type is not allowed
    """
    from .models import Attachment
    
    # Get file extension
    import os
    file_extension = os.path.splitext(file_obj.name)[1].lower().lstrip('.')
    
    if file_extension not in Attachment.ALLOWED_EXTENSIONS:
        raise ValidationError(
            _('File type "%(file_type)s" is not allowed. Allowed types: %(allowed_types)s'),
            params={
                'file_type': file_extension,
                'allowed_types': ', '.join(Attachment.ALLOWED_EXTENSIONS)
            }
        )


def validate_attachment(file_obj):
    """
    Combined validation for file size and content type.
    
    Args:
        file_obj: Django UploadedFile object
        
    Raises:
        ValidationError: If file doesn't meet requirements
    """
    validate_file_size(file_obj)
    validate_content_type(file_obj)

