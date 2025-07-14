# tests/test_retry.py

import time
import requests
from utils.retry import retry_with_backoff

calls = []

@retry_with_backoff(max_retries=3, backoff_factor=1.2)
def simulated_failing_request():
    calls.append(time.time())
    response = requests.get("https://httpbin.org/status/503")  # Always returns 503
    response.raise_for_status()

    

def test_retry_backoff_behavior():
    start = time.time()
    try:
        simulated_failing_request()
    except requests.exceptions.HTTPError:
        duration = time.time() - start
        print(f"Retry sequence took {duration:.2f} seconds")
        assert len(calls) == 3  # Should have tried 3 times
        assert duration >= 1.2 + 1.2**2  # Rough minimum backoff time
    else:
        assert False, "Expected an HTTPError but none was raised"
