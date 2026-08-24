"""Short-lived, bounded store of answers that have not been persisted yet.

Exists because of the `log_questions: false` mode: there, an interaction
must only reach the database if a human actually reacts to it. The client
cannot be asked to send the question/answer/sources back with the reaction
-- that is forgeable, bulky, and drifts from what the server really did --
so the server keeps its own copy for a while and writes it at reaction
time instead.

Bounded on both axes so a busy day cannot grow it without limit: oldest
entries fall out past `maxsize`, and anything older than `ttl_seconds` is
dropped on access.
"""
import time
from collections import OrderedDict


class InteractionCache:
    def __init__(self, maxsize: int = 1000, ttl_seconds: int = 7200):
        self._maxsize = maxsize
        self._ttl = ttl_seconds
        self._items: OrderedDict[str, tuple[float, dict]] = OrderedDict()

    def put(self, key: str, payload: dict) -> None:
        self._items[key] = (time.monotonic(), payload)
        self._items.move_to_end(key)
        while len(self._items) > self._maxsize:
            self._items.popitem(last=False)

    def pop(self, key: str) -> dict | None:
        """Take an entry out; None if unknown or expired.

        Removing on read is deliberate: once persisted, the row lives in the
        database and a second reaction should update that row rather than
        re-insert from a stale copy.
        """
        self._evict_expired()
        item = self._items.pop(key, None)
        return item[1] if item else None

    def get(self, key: str) -> dict | None:
        self._evict_expired()
        item = self._items.get(key)
        return item[1] if item else None

    def _evict_expired(self) -> None:
        cutoff = time.monotonic() - self._ttl
        while self._items:
            key, (stamp, _) = next(iter(self._items.items()))
            if stamp >= cutoff:
                break
            self._items.popitem(last=False)

    def __len__(self) -> int:
        self._evict_expired()
        return len(self._items)
