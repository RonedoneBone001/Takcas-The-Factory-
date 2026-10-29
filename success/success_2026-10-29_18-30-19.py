import threading
from collections import OrderedDict
import time

class LRUCache:
    def __init__(self, capacity: int, default_ttl: int = 60, cleanup_interval: float = 1.0):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval
        self.expirations = 0
        self.callback_lock = threading.Lock()
        self.callback_called = threading.local()

        # Start a thread to clean up expired entries
        self.cleanup_thread = threading.Thread(target=self.cleanup_expired_entries)
        self.cleanup_thread.daemon = True
        self.cleanup_thread.start()

    def get(self, key):
        with self.lock:
            if key in self.cache:
                self.hits += 1
                self.cache.move_to_end(key)
                self.callback_called = threading.local()
                expiry_time = self.cache[key][1]
                if time.time() < expiry_time:
                    return self.cache[key][0]
                else:
                    self.evictions += 1
                    self.callback_on_evict(key, self.cache[key][0])
                    self.cache.pop(key)
                    self.expirations += 1
                    return None
            else:
                self.misses += 1
                self.callback_called = threading.local()
                return None

    def put(self, key, value, ttl=None):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                if len(self.cache) == self.capacity:
                    self.cache.popitem(last=False)
                    self.evictions += 1
            if ttl is not None:
                expiry_time = time.time() + ttl
            else:
                expiry_time = time.time() + self.default_ttl
            self.cache[key] = (value, expiry_time)
            self.cache.move_to_end(key)

    def callback_on_evict(self, key, value):
        if not self.callback_called:
            with self.callback_lock:
                self.callback_called = threading.local()
                self.callback(key, value)

    def cleanup_expired_entries(self):
        while True:
            with self.lock:
                current_time = time.time()
                expired_items = [key for key, (value, expiry_time) in self.cache.items() if expiry_time < current_time]
                for key in expired_items:
                    self.cache.pop(key)
                    self.expirations += 1
                    self.callback_on_evict(key, self.cache[key][0])
            time.sleep(self.cleanup_interval)

    def on_evict(self, key, value):
        print(f"Evicted: key={key}, value={value}")

    def test_lru_cache(self):
        cache = LRUCache(capacity=3, default_ttl=0.1, cleanup_interval=0.5)
        threads = []

        def worker():
            for i in range(100):
                key = i % 5
                if i % 2 == 0:
                    cache.put(key, f"value{i}", ttl=0.2)
                else:
                    cache.get(key)

        for i in range(4):
            threads.append(threading.Thread(target=worker))
            threads[-1].start()

        for thread in threads:
            thread.join()

        print("Hits:", cache.hits)
        print("Misses:", cache.misses)
        print("Evictions:", cache.evictions)
        print("Expirations:", cache.expirations)

if __name__ == "__main__":
    test_lru_cache()