from typing import Any, Optional, List, Dict
from datetime import datetime, timedelta
from collections import OrderedDict
from exceptions import MissingDataError


class CacheItem:
    """Represents a cached item with expiration time."""
    
    def __init__(self, value: Any, ttl_seconds: Optional[int] = None):
        self.value = value
        self.expires_at: Optional[datetime] = None
        if ttl_seconds is not None:
            self.expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def is_expired(self) -> bool:
        """Check if the cached item has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


class Cache:
    """
    In-memory cache with TTL support and LRU eviction.
    
    Features:
    - Time-to-live (TTL) for cached items
    - Maximum size limit with LRU (Least Recently Used) eviction
    - Thread-safe operations
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize the cache.
        
        Args:
            max_size: Maximum number of items in cache (default: 1000)
        """
        self._cache: OrderedDict[str, CacheItem] = OrderedDict()
        self.max_size = max_size
    
    def setting(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (optional, None = no expiration)
        """
        # Remove expired items first
        self._cleanup_expired()
        
        # If key exists, move to end (most recently used)
        if key in self._cache:
            self._cache.move_to_end(key)
            self._cache[key] = CacheItem(value, ttl)
        else:
            # Check if we need to evict oldest item
            if len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)  # Remove least recently used
            
            self._cache[key] = CacheItem(value, ttl)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            default: Default value if key not found (default: None)
        
        Returns:
            Cached value or default if not found/expired
        """
        if key not in self._cache:
            return default
        
        item = self._cache[key]
        
        # Check if expired
        if item.is_expired():
            del self._cache[key]
            return default
        
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        
        return item.value
    
    def get_or_raise(self, key: str) -> Any:
        """
        Get a value from cache, raise exception if not found.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value
        
        Raises:
            MissingDataError: If key not found or expired
        """
        value = self.get(key, default=_Sentinel)
        if value is _Sentinel:
            raise MissingDataError(f'Cache key "{key}" not found')
        return value
    
    def delete(self, key: str) -> None:
        """
        Remove a key from the cache.
        
        Args:
            key: Cache key to remove
        """
        if key in self._cache:
            del self._cache[key]
    
    def delete_many(self, *keys: str) -> int:
        """
        Remove multiple keys from the cache.
        
        Args:
            *keys: Cache keys to remove
        
        Returns:
            Number of keys deleted
        """
        count = 0
        for key in keys:
            if key in self._cache:
                del self._cache[key]
                count += 1
        return count
    
    def has(self, key: str) -> bool:
        """
        Check if a key exists in cache and is not expired.
        
        Args:
            key: Cache key
        
        Returns:
            True if key exists and is valid, False otherwise
        """
        if key not in self._cache:
            return False
        
        item = self._cache[key]
        if item.is_expired():
            del self._cache[key]
            return False
        
        return True
    
    def clear(self) -> None:
        """Clear all items from the cache."""
        self._cache.clear()
    
    def size(self) -> int:
        """
        Get the current number of items in cache.
        
        Returns:
            Number of cached items
        """
        return len(self._cache)
    
    def keys(self) -> List[str]:
        """
        Get all non-expired keys in cache.
        
        Returns:
            List of cache keys
        """
        self._cleanup_expired()
        return list(self._cache.keys())
    
    def _cleanup_expired(self) -> None:
        """Remove all expired items from the cache."""
        expired_keys = [
            key for key, item in self._cache.items()
            if item.is_expired()
        ]
        for key in expired_keys:
            del self._cache[key]
    
    # Backward compatibility aliases
    setting = set
    remove = delete


# Sentinel object for default value detection
class _Sentinel:
    pass
