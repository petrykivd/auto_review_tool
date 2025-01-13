from typing import TypeVar, Callable, Any, Set, Type
from functools import wraps
import time
from loguru import logger

from src.core.exceptions import BaseAPIError

T = TypeVar('T')


def retry_with_backoff(
    retries: int = 3,
    backoff_factor: float = 1.5,
    status_forcelist: Set[int] = {429, 500, 502, 503, 504},
    exceptions: tuple[Type[Exception], ...] = (BaseAPIError,)
) -> Callable:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            retry_count = 0
            wait_time = 1

            while retry_count < retries:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    status_code = getattr(e, 'status_code', None)
                    retry_after = getattr(e, 'retry_after', None)

                    if status_code and status_code in status_forcelist:
                        if status_code == 429 and retry_after:
                            logger.warning(
                                f"Rate limit exceeded. Waiting {retry_after} seconds."
                            )
                            time.sleep(retry_after)
                        else:
                            logger.warning(
                                f"Request failed with status {status_code}. "
                                f"Retrying in {wait_time} seconds..."
                            )
                            time.sleep(wait_time)

                        wait_time *= backoff_factor
                        retry_count += 1

                        if retry_count == retries:
                            logger.error(
                                f"Max retries ({retries}) reached. "
                                f"Last error: {str(e)}"
                            )
                            raise
                    else:
                        raise
                except Exception as e:
                    logger.error(f"Unexpected error: {str(e)}")
                    raise

            return await func(*args, **kwargs)

        return wrapper

    return decorator
