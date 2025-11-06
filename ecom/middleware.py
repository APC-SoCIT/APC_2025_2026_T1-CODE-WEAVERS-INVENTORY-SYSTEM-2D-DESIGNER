from django.utils.deprecation import MiddlewareMixin


class DBReadinessMiddleware(MiddlewareMixin):
    """No-op middleware: allows all requests and exceptions to pass through."""

    def process_request(self, request):
        return None

    def process_exception(self, request, exception):
        return None

