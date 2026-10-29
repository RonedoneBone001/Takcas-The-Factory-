import threading
import time
from collections import OrderedDict

class TTLCache:
    def __init__(self, capacity: int, default_ttl: float, cleanup_interval:[17D[K
cleanup_interval: float):
        self.capacity = capacity
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval
        self.cache = OrderedDict()
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expirations = 0
        self.on_evict = None

    def get(self, key):
        with self.lock:
            if key in self.cache:
                self.hits += 1
                self._update_ttl(key)
                return self.cache[key]
            else:
                self.misses += 1
                return None

    def put(self, key, value, ttl=None):
        with self.lock:
            if key in self.cache:
                self.evictions += 1
                self.cache.pop(key)
            self._update_ttl(key, ttl or self.default_ttl)
            self.cache[key] = value
            if len(self.cache) > self.capacity:
                self._evict_lru()

    def _update_ttl(self, key, ttl=None):
        if ttl is not None:
            self.cache.move_to_end(key, last=False)
        else:
            self.cache.move_to_end(key)

    def _evict_lru(self):
        with self.lock:
            while len(self.cache) > self.capacity:
                key, _ = self.cache.popitem(last=False)
                self.expirations += 1
                if self.on_evict:
                    self.on_evict(key, self.cache[key], "lru")

    def start_cleanup(self):
        while True:
            with self.lock:
                if time.time() - self.last_cleanup > self.cleanup_interval:[22D[K
self.cleanup_interval:
                    self._evict_expired()
            time.sleep(self.cleanup_interval)

    def _evict_expired(self):
        with self.lock:
            for key in list(self.cache.keys()):
                if time.time() - self.cache[key] > self.default_ttl:
                    self.evictions += 1
                    if self.on_evict:
                        self.on_evict(key, self.cache[key], "ttl")
                    self.cache.pop(key)

    def get_stats(self):
        with self.lock:
            return {
                "hits": self.hits,
                "misses": self.misses,
                "evictions": self.evictions,
                "expirations": self.expirations,
                "size": len(self.cache),
                "hit_ratio": self.hits / (self.hits + self.misses) if self.[5D[K
self.hits + self.misses > 0 else 0
            }

    def set_on_evict(self, callback):
        self.on_evict = callback

# Тест
if __name__ == "__main__":
    cache = TTLCache(capacity=100, default_ttl=0.5, cleanup_interval=0.1)
    cache.set_on_evict(lambda key, value, reason: print(f"Evicted: {key} du[2D[K
due to {reason}"))

    threads = []
    for _ in range(8):
        thread = threading.Thread(target=lambda: [
            cache.get(i % 50),
            cache.put(i % 50, i, 0.05 + 0.15 * (i % 50))
            for i in range(500)
        ])
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    stats = cache.get_stats()
    assert stats["hits"] + stats["misses"] == 4000
    assert stats["size"] <= 100
    assert not cache.on_evict_called  # Проверка того, что on_evict не вызы[4D[K
вызывался под локом

    print(stats)