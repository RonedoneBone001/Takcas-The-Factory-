import threading
from collections import OrderedDict
import time

class LRUCache:
    def __init__(self, capacity: int, default_ttl: float, cleanup_interval: float, on_evict=None):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expirations = 0
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval
        self.on_evict = on_evict
        self.cleanup_thread = threading.Timer(self.cleanup_interval, self.cleanup)

    def get(self, key):
        with self.lock:
            if key in self.cache:
                value, expiry_time = self.cache[key]
                if expiry_time > time.time():
                    self.hits += 1
                    self.cache.move_to_end(key)
                    return value
                else:
                    self.misses += 1
                    self.cache.pop(key)
                    self.expirations += 1
                    if self.on_evict:
                        self.on_evict(key, reason="ttl")
                    return None
            else:
                self.misses += 1
                return None

    def put(self, key, value, ttl=None):
        if ttl is None:
            ttl = self.default_ttl
        evicted = None
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                self.cache[key] = (value, time.time() + ttl)
            else:
                if len(self.cache) >= self.capacity:
                    evicted_key, _ = self.cache.popitem(last=False)
                    self.evictions += 1
                    evicted = (evicted_key, None)
                self.cache[key] = (value, time.time() + ttl)

        # Вызываем callback ВНЕ лока
        if evicted and self.on_evict:
            self.on_evict(evicted[0], reason="eviction")

    def cleanup(self):
        with self.lock:
            for key, (value, expiry_time) in self.cache.items():
                if expiry_time and expiry_time < time.time():
                    self.misses += 1
                    self.cache.pop(key)
                    self.expirations += 1
                    if self.on_evict:
                        self.on_evict(key, reason="ttl")
        self.cleanup_thread = threading.Timer(self.cleanup_interval, self.cleanup)
        self.cleanup_thread.start()

def test_lru_cache():
    callback_under_lock = threading.local()
    callback_under_lock.is_locked = False

    def on_evict(key, reason):
        # Пытаемся захватить лок. Если получается - значит, мы ВНЕ лока.
        if cache.lock.acquire(blocking=False):
            cache.lock.release()
            callback_under_lock.is_locked = False
        else:
            callback_under_lock.is_locked = True

    cache = LRUCache(capacity=3, default_ttl=0.2, cleanup_interval=0.5, on_evict=on_evict)
    threads = []

    def worker():
        for i in range(80):
            key = i % 5
            if i % 2 == 0:
                cache.put(key, f"value{i}", ttl=0.1)
            else:
                cache.get(key)

    for _ in range(4):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("Hits:", cache.hits)
    print("Misses:", cache.misses)
    print("Evictions:", cache.evictions)
    print("Expirations:", cache.expirations)
    print("Callback called under lock:", callback_under_lock.is_locked)
    assert not callback_under_lock.is_locked, "Callback was called under lock!"
    print("Test passed successfully!")

if __name__ == "__main__":
    test_lru_cache()