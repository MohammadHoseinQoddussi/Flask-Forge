from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Any, List, Optional

from .exceptions import MissingDataError


class CacheItem:
    def __init__(self, value: Any, ttl_seconds: Optional[int] = None):
        self.value = value
        self.expires_at: Optional[datetime] = None
        if ttl_seconds is not None:
            self.expires_at = datetime.now() + timedelta(seconds=ttl_seconds)

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


class _SentinelType:
    pass


_Sentinel = _SentinelType()


class Cache:
    """In-memory cache with TTL support and LRU eviction."""

    def __init__(self, max_size: int = 1000):
        self._cache: OrderedDict[str, CacheItem] = OrderedDict()
        self.max_size = max_size

    def setting(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        self._cleanup_expired()
        if key in self._cache:
            self._cache.move_to_end(key)
            self._cache[key] = CacheItem(value, ttl)
        else:
            if len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)
            self._cache[key] = CacheItem(value, ttl)

    set = setting

    def get(self, key: str, default: Any = None) -> Any:
        if key not in self._cache:
            return default
        item = self._cache[key]
        if item.is_expired():
            del self._cache[key]
            return default
        self._cache.move_to_end(key)
        return item.value

    def get_or_raise(self, key: str) -> Any:
        value = self.get(key, default=_Sentinel)
        if value is _Sentinel:
            raise MissingDataError(f'Cache key "{key}" not found')
        return value

    def delete(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]

    remove = delete

    def delete_many(self, *keys: str) -> int:
        count = 0
        for key in keys:
            if key in self._cache:
                del self._cache[key]
                count += 1
        return count

    def has(self, key: str) -> bool:
        if key not in self._cache:
            return False
        item = self._cache[key]
        if item.is_expired():
            del self._cache[key]
            return False
        return True

    def clear(self) -> None:
        self._cache.clear()

    def size(self) -> int:
        self._cleanup_expired()
        return len(self._cache)

    def keys(self) -> List[str]:
        self._cleanup_expired()
        return list(self._cache.keys())

    def _cleanup_expired(self) -> None:
        expired_keys = [
            key for key, item in self._cache.items() if item.is_expired()
        ]
        for key in expired_keys:
            del self._cache[key]
