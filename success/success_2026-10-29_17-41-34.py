import threading
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.callback_lock = threading.Lock()
        self.callback_called = threading.local()

    def get(self, key):
        with self.lock:
            if key in self.cache:
                self.hits += 1
                self.cache.move_to_end(key)
                self.callback_called = threading.local()
                return self.cache[key]
            else:
                self.misses += 1
                self.callback_called = threading.local()
                return None

    def put(self, key, value):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                if len(self.cache) == self.capacity:
                    self.cache.popitem(last=False)
                    self.evictions += 1
            self.cache[key] = value
            self.cache.move_to_end(key)

    def callback_on_evict(self, key, value):
        if not self.callback_called:
            with self.callback_lock:
                self.callback_called = threading.local()
                self.callback(key, value)

    def test_lru_cache(self):
        cache = LRUCache(capacity=3)
        threads = []

        def worker():
            for i in range(100):
                key = i % 5
                if i % 2 == 0:
                    cache.put(key, f"value{i}")
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

    def on_evict(self, key, value):
        print(f"Evicted: key={key}, value={value}")

if __name__ == "__main__":
    test_lru_cache()