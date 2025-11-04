import logging
from functools import wraps

logger = logging.getLogger(__name__)


def exception_suppress(exception_type=Exception, default=None, logger=logger, loglevel=logging.WARNING):
    def wrapper(f):
        @wraps(f)
        def sync_decorator(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except exception_type as e:
                logger.log(loglevel, f"Suppressed exception: {e}")
                return default

        return sync_decorator

    return wrapper

def async_exception_suppress(exception_type=Exception, default=None, logger=logger, loglevel=logging.WARNING):
    def wrapper(f):
        @wraps(f)
        async def async_decorator(*args, **kwargs):
            try:
                return await f(*args, **kwargs)
            except exception_type as e:
                logger.log(loglevel, f"Suppressed exception: {e}")
                return default

        return async_decorator

    return wrapper
