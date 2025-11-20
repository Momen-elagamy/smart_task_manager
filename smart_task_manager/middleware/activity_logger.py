import logging
logger = logging.getLogger('smart_task_manager')

class ActivityLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        response = self.get_response(request)
        logger.info(
            f"User: {user if user and user.is_authenticated else 'Anonymous'} | "
            f"Method: {request.method} | Path: {request.path} | Status: {response.status_code}"
        )
        return response
