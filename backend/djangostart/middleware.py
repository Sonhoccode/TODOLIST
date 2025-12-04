# djangostart/middleware.py
import time
import logging

logger = logging.getLogger(__name__)

class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = (time.time() - start) * 1000  # ms

        logger.info(
            "[PERF] %s %s took %.1f ms",
            request.method,
            request.path,
            duration,
        )

        return response
