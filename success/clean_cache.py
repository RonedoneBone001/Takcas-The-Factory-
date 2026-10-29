import threading
import time
from collections import OrderedDict


class TTLCache:
    def __init__(self, capacity, default_ttl, cleanup_interval):
        self.capacity = capacity
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval
        self.cache = OrderedDict()
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expirations = 0
        self.on_evict = None
        self._stop_event = threading.Event()
        self._cleaner_thread = None

    def get(self, key):
        victims = []
        with self.lock:
            item = self.cache.get(key)
            if item is None:
                self.misses += 1
                result = None
            else:
                value, expires_at = item
                if expires_at is not None and time.monotonic() >= expires_at:
                    self.cache.pop(key)
                    self.expirations += 1
                    self.misses += 1
                    victims.append((key, value, "ttl"))
                    result = None
                else:
                    self.hits += 1
                    self.cache.move_to_end(key)
                    result = value
        self._fire_callbacks(victims)
        return result

    def put(self, key, value, ttl=None):
        victims = []
        ttl = self.default_ttl if ttl is None else ttl
        expires_at = (time.monotonic() + ttl) if ttl is not None else None
        with self.lock:
            if key in self.cache:
                self.cache.pop(key)
            self.cache[key] = (value, expires_at)
            while len(self.cache) > self.capacity:
                old_key, (old_value, _) = self.cache.popitem(last=False)
                self.evictions += 1
                victims.append((old_key, old_value, "lru"))
        self._fire_callbacks(victims)

    def get_stats(self):
        with self.lock:
            total = self.hits + self.misses
            return {
                "hits": self.hits,
                "misses": self.misses,
                "evictions": self.evictions,
                "expirations": self.expirations,
                "size": len(self.cache),
                "hit_ratio": self.hits / total if total else 0.0,
            }

    def set_on_evict(self, callback):
        with self.lock:
            self.on_evict = callback

    def start_cleanup(self):
        if self._cleaner_thread is not None:
            return
        self._cleaner_thread = threading.Thread(
            target=self._cleanup_loop, daemon=True
        )
        self._cleaner_thread.start()

    def stop_cleanup(self):
        self._stop_event.set()
        if self._cleaner_thread is not None:
            self._cleaner_thread.join(timeout=2.0)
            self._cleaner_thread = None

    def _cleanup_loop(self):
        while not self._stop_event.wait(self.cleanup_interval):
            self._cleanup_once()

    def _cleanup_once(self):
        now = time.monotonic()
        expired = []
        with self.lock:
            for key, (value, expires_at) in list(self.cache.items()):
                if expires_at is not None and now >= expires_at:
                    self.cache.pop(key)
                    self.expirations += 1
                    expired.append((key, value, "ttl"))
        self._fire_callbacks(expired)

    def _fire_callbacks(self, victims):
        cb = self.on_evict
        if cb is None:
            return
        for key, value, reason in victims:
            try:
                cb(key, value, reason)
            except Exception:
                pass


def main():
    import random

    cache = TTLCache(capacity=100, default_ttl=0.5, cleanup_interval=0.1)

    violations = []
    vlock = threading.Lock()

    def on_evict(key, value, reason):
        if cache.lock.locked():
            with vlock:
                violations.append((key, reason))

    cache.set_on_evict(on_evict)
    cache.start_cleanup()

    THREADS = 8
    OPS = 500
    KEYS = 50
    total_gets_counter = [0]
    gets_lock = threading.Lock()

    def worker(seed):
        rnd = random.Random(seed)
        local_gets = 0
        for _ in range(OPS):
            key = rnd.randrange(KEYS)
            if rnd.random() < 0.5:
                cache.get(key)
                local_gets += 1
            else:
                ttl = rnd.choice([0.05, 0.1, 0.2, 0.5, None])
                cache.put(key, key, ttl=ttl)
        with gets_lock:
            total_gets_counter[0] += local_gets

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    cache.stop_cleanup()
    stats = cache.get_stats()
    print("Stats:", stats)

    total_gets = total_gets_counter[0]
    assert stats["hits"] + stats["misses"] == total_gets, (
        "hits+misses=%d != total_gets=%d" % (
            stats["hits"] + stats["misses"], total_gets
        )
    )
    assert stats["size"] <= cache.capacity, (
        "size=%d > capacity=%d" % (stats["size"], cache.capacity)
    )
    assert not violations, "callback under lock: %r" % (violations[:5],)
    print("OK: all invariants satisfied")


if __name__ == "__main__":
    main()
