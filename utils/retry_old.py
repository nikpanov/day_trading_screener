
import time
import functools
import logging

def retry_with_backoff(max_retries=3, backoff_factor=1.5, exceptions=(Exception,), logger=None):
    """
    Decorator for retrying a function with exponential backoff.

    Args:
        max_retries (int): Maximum number of retry attempts.
        backoff_factor (float): Factor for exponential wait time.
        exceptions (tuple): Exception types to trigger retry.
        logger (logging.Logger): Optional logger for error output.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    wait_time = backoff_factor ** attempt
                    msg = f"[{func.__name__}] Attempt {attempt+1} failed: {e}. Retrying in {wait_time:.1f}s..."
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(wait_time)
            raise last_exception  # ← this is the fix
        return wrapper
    return decorator
