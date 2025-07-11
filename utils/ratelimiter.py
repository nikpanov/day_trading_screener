# utils/ratelimiter.py
import threading
import time

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.lock = threading.Lock()
        self.calls = []
    
    def wait(self):
        with self.lock:
            now = time.time()
            # Remove old timestamps
            self.calls = [t for t in self.calls if now - t < self.period]

            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0])
                time.sleep(max(0, sleep_time))

            self.calls.append(time.time())
