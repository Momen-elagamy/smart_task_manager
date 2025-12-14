"""
Middleware to exempt API endpoints from CSRF verification when using JWT authentication.
This allows API calls with JWT tokens to work without CSRF tokens.
"""

from django.utils.deprecation import MiddlewareMixin


class CSRFExemptAPIMiddleware(MiddlewareMixin):
    """
    Middleware that exempts API endpoints from CSRF verification
    when the request includes a valid JWT Authorization header.
    """
    
    def process_request(self, request):
        # Check if this is an API request (core or chat namespace)
        if request.path.startswith('/api/') or request.path.startswith('/chat/api/'):
            # Check if request has Authorization header (JWT)
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                # Mark request as CSRF exempt
                setattr(request, '_dont_enforce_csrf_checks', True)
