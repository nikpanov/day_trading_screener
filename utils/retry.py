import time
import random
import logging
import requests
from functools import wraps
import functools

logger = logging.getLogger("screener")

def retry_on_429(
    max_retries=5,
    base_delay=1.0,
    backoff_factor=1.5,
    jitter=0.3,
    logger=None
):
    """
    Retry decorator to handle HTTP 429 Too Many Requests errors
    with exponential backoff and optional jitter.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.HTTPError as e:
                    response = getattr(e, "response", None)
                    if response is not None and response.status_code == 429:
                        retry_after = response.headers.get("Retry-After")
                        if retry_after is not None:
                            delay = float(retry_after)
                            logger.warning(f"[{func.__name__}] 429 Too Many Requests. Retrying in {delay:.1f}s (from Retry-After header)...")
                        else:
                            delay = base_delay * (backoff_factor ** (attempt - 1))
                            delay += random.uniform(0, jitter)
                            logger.warning(f"[{func.__name__}] 429 Too Many Requests. Retrying in {delay:.1f}s (exponential backoff)...")
                        time.sleep(delay)
                    else:
                        raise  # Reraise other errors
            raise RuntimeError(f"[{func.__name__}] Failed after {max_retries} retries due to repeated 429s.")
        return wrapper
    return decorator

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