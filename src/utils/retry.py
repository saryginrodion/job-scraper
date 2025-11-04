import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps

logger = logging.getLogger(__name__)


@dataclass
class RetryContext:
    retry_attempt: int
    exception: Exception | None


def async_retry(retries: int = 3, delay_func: Callable[[RetryContext], float] = lambda ctx: float(3 * ctx.retry_attempt)):
    def wrapper(f):
        @wraps(f)
        async def decorator(*args, **kwargs):
            last_exc: Exception | None = None

            for attempt in range(1, retries + 1):
                ctx = RetryContext(attempt, last_exc)
                try:
                    return await f(*args, **kwargs)
                except Exception as e:
                    last_exc = e

                    if attempt == retries:
                        logger.debug(f"Retry limits exhausted. Exception: {e}")  # noqa: G004
                        raise

                    await asyncio.sleep(delay_func(ctx))

            raise last_exc  # type: ignore

        return decorator
    return wrapper
