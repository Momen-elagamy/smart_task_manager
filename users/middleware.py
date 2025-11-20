from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser
from datetime import datetime, timedelta


class RememberMeMiddleware(MiddlewareMixin):
    """
    Middleware to automatically authenticate users from cookies when remember_me was enabled
    """
    
    def process_request(self, request):
        # Skip if user is already authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            return None
        
        # Skip if on logout pages - IMPORTANT: don't authenticate on logout
        if request.path in ['/logout/', '/api/users/logout/']:
            request.user = AnonymousUser()
            return None
        
        # Skip on login/register/forgot-password pages - these are PUBLIC pages
        public_paths = [
            '/login/',
            '/register/', 
            '/forgot-password/',
            '/api/users/login/', 
            '/api/token/',
            '/api/users/register/',
            '/api/users/request-password-reset/',
            '/api/users/verify-otp/',
            '/api/users/reset-password/',
        ]
        
        if request.path in public_paths or any(request.path.startswith(path) for path in public_paths):
            return None
        
        # Check for access token in cookies
        access_token = request.COOKIES.get('access_token')
        
        if not access_token:
            # No token found, user stays as AnonymousUser
            return None
        
        try:
            # Try to authenticate using the token from cookie
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(access_token)
            user = jwt_auth.get_user(validated_token)
            
            # Set the user on the request
            request.user = user
            
            # Add the token to the Authorization header for API views
            if not request.META.get('HTTP_AUTHORIZATION'):
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
                
        except (InvalidToken, TokenError) as e:
            # Token is invalid or expired
            # Make sure user is AnonymousUser
            request.user = AnonymousUser()
            # Don't set Authorization header if token is invalid
            if 'HTTP_AUTHORIZATION' in request.META:
                del request.META['HTTP_AUTHORIZATION']
        except Exception as e:
            # Any other error, treat as unauthenticated
            request.user = AnonymousUser()
        
        return None
