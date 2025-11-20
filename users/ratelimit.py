"""
Rate Limiting Middleware and Decorators
"""
from django.core.cache import cache
from django.http import JsonResponse
from functools import wraps
import time


class RateLimitMiddleware:
    """Global rate limiting middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip rate limiting for static files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)
        
        response = self.get_response(request)
        return response


def rate_limit(key_prefix, rate, period):
    """
    Rate limit decorator for views.
    
    Args:
        key_prefix: Prefix for cache key (e.g., 'login')
        rate: Number of allowed requests
        period: Time period in seconds
    
    Example:
        @rate_limit('login', rate=5, period=300)  # 5 requests per 5 minutes
        def login_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Get identifier (IP or user)
            identifier = request.user.id if request.user.is_authenticated else request.META.get('REMOTE_ADDR', 'unknown')
            cache_key = f'ratelimit:{key_prefix}:{identifier}'
            
            # Get current request data
            request_data = cache.get(cache_key, {'count': 0, 'reset_at': time.time() + period})
            
            # Check if period has expired
            if time.time() > request_data['reset_at']:
                request_data = {'count': 0, 'reset_at': time.time() + period}
            
            # Check rate limit
            if request_data['count'] >= rate:
                retry_after = int(request_data['reset_at'] - time.time())
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'retry_after': retry_after,
                    'limit': rate,
                    'period': period
                }, status=429)
            
            # Increment counter
            request_data['count'] += 1
            cache.set(cache_key, request_data, period)
            
            # Add rate limit headers to response
            response = view_func(request, *args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = str(rate)
                response.headers['X-RateLimit-Remaining'] = str(rate - request_data['count'])
                response.headers['X-RateLimit-Reset'] = str(int(request_data['reset_at']))
            
            return response
        
        return wrapper
    return decorator


def get_rate_limit_status(request, key_prefix):
    """
    Get current rate limit status for a user/IP.
    
    Returns:
        dict: {count, limit, remaining, reset_at}
    """
    identifier = request.user.id if request.user.is_authenticated else request.META.get('REMOTE_ADDR', 'unknown')
    cache_key = f'ratelimit:{key_prefix}:{identifier}'
    
    request_data = cache.get(cache_key)
    if not request_data:
        return {'count': 0, 'remaining': None, 'reset_at': None}
    
    return {
        'count': request_data['count'],
        'reset_at': request_data['reset_at']
    }
