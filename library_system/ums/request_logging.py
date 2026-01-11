import logging
import contextvars
import uuid
import threading

# Context variable that holds the current request id for the execution context.
request_id_var: contextvars.ContextVar = contextvars.ContextVar('request_id', default=None)


class RequestIDFilter(logging.Filter):
    """Logging filter that injects `request_id` into LogRecord.

    This uses a ContextVar so the value is available to the current context
    (and can be explicitly propagated to new threads using
    `run_in_thread_with_context`).
    """

    def filter(self, record):
        rid = request_id_var.get()
        record.request_id = rid if rid is not None else '-'
        return True


def generate_request_id() -> str:
    return str(uuid.uuid4())


def set_request_id(rid: str | None = None) -> str:
    """Set the request id for the current context and return it."""
    if rid is None:
        rid = generate_request_id()
    request_id_var.set(rid)
    return rid


def get_request_id() -> str | None:
    return request_id_var.get()


def run_in_thread_with_context(target, *args, daemon: bool = False, **kwargs) -> threading.Thread:
    """Run `target(*args, **kwargs)` in a new Thread while preserving the
    current context (including `request_id`). Returns the Thread object.

    Usage:
        from ums.request_logging import run_in_thread_with_context

        def background_task(arg):
            import logging
            logger = logging.getLogger(__name__)
            logger.info("running background task")

        run_in_thread_with_context(background_task, 123)
    """

    ctx = contextvars.copy_context()

    def _run():
        ctx.run(target, *args, **kwargs)

    t = threading.Thread(target=_run, daemon=daemon)
    t.start()
    return t
