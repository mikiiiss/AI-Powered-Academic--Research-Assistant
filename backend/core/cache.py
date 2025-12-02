# backend/core/cache.py
import redis
import json
import hashlib
import os
from typing import Any, Optional
from functools import wraps

class CacheManager:
    def __init__(self):
        # Redis connection with fallback
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        redis_db = int(os.getenv('REDIS_DB', 0))
        
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True,
                socket_connect_timeout=2
            )
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            print("✅ Redis cache connected")
        except (redis.ConnectionError, redis.TimeoutError) as e:
            print(f"⚠️ Redis not available: {e}")
            print("   Cache disabled - operations will proceed without caching")
            self.redis_client = None
            self.enabled = False
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a unique cache key from function arguments"""
        # Create a string representation of args and kwargs
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        # Hash it for consistent key length
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def get_cached(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            cached = self.redis_client.get(key)
            if cached:
                print(f"   💾 Cache HIT for key: {key[:50]}...")
                return json.loads(cached)
            print(f"   ❌ Cache MISS for key: {key[:50]}...")
            return None
        except Exception as e:
            print(f"   ⚠️ Cache get error: {e}")
            return None
    
    def set_cached(self, key: str, value: Any, ttl: int = 3600):
        """Set cached value with TTL (time to live) in seconds"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            serialized = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
            print(f"   💾 Cached for {ttl}s: {key[:50]}...")
            return True
        except Exception as e:
            print(f"   ⚠️ Cache set error: {e}")
            return False
    
    def invalidate(self, pattern: str):
        """Invalidate cache keys matching pattern"""
        if not self.enabled or not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                print(f"   🗑️ Invalidated {deleted} cache entries")
                return deleted
            return 0
        except Exception as e:
            print(f"   ⚠️ Cache invalidation error: {e}")
            return 0

# Global cache instance
cache_manager = CacheManager()
