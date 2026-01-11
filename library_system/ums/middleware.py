from typing import Callable

from . import request_logging


class RequestIDMiddleware:
    """Middleware that assigns a UUID to each incoming request and stores it
    in a ContextVar so logs automatically include it.

    The middleware also adds `request.request_id` and sets the
    `X-Request-ID` response header. For background threads, use
    `ums.request_logging.run_in_thread_with_context(...)` to preserve the
    request context in the new thread.
    """

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request):
        rid = request_logging.set_request_id()
        request.request_id = rid

        response = self.get_response(request)
        # expose request id to clients
        try:
            response['X-Request-ID'] = rid
        except Exception:
            pass

        # clear request id for this context to avoid leaking between requests
        request_logging.request_id_var.set(None)

        return response
