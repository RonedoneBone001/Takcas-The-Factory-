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

    def get(self, key):
        with self.lock:
            if key in self.cache:
                self.hits += 1
                self.cache.move_to_end(key)
                return self.cache[key]
            else:
                self.misses += 1
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

def test_lru_cache():
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

if __name__ == "__main__":
    test_lru_cache()