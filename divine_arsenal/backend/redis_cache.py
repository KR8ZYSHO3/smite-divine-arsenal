#!/usr/bin/env python3
"""
Redis Caching Configuration for SMITE 2 Divine Arsenal
Optimizes performance for high-traffic queries
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Union
from functools import wraps

try:
    import redis
    from flask import current_app
    Redis = redis.Redis
except ImportError:
    redis = None
    Redis = None

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis caching wrapper for Divine Arsenal."""
    
    def __init__(self, redis_url: Optional[str] = None, default_timeout: int = 300):
        """Initialize Redis cache."""
        self.redis_client: Optional[Any] = None
        self.default_timeout = default_timeout
        self.enabled = False
        
        if redis:
            try:
                redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379')
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                self.redis_client.ping()
                self.enabled = True
                logger.info("✅ Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ Redis unavailable, caching disabled: {e}")
        else:
            logger.warning("⚠️ Redis not installed, caching disabled")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
        return None
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Set value in cache."""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            timeout = timeout or self.default_timeout
            serialized_value = json.dumps(value, default=str)
            return self.redis_client.setex(key, timeout, serialized_value)
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if not self.enabled or not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
        return 0


# Global cache instance
cache = RedisCache()


def cached(timeout: int = 300, key_prefix: str = ""):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            cache.set(cache_key, result, timeout)
            logger.debug(f"Cache set for {func.__name__}")
            
            return result
        return wrapper
    return decorator


def cache_gods_data(func):
    """Specific decorator for gods data caching."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        cache_key = "gods:all_gods"
        
        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.debug("Cache hit for gods data")
            return cached_result
        
        # Get fresh data
        result = func(*args, **kwargs)
        
        # Cache for 10 minutes (gods data doesn't change often)
        cache.set(cache_key, result, 600)
        logger.debug("Gods data cached for 10 minutes")
        
        return result
    return wrapper


def cache_items_data(func):
    """Specific decorator for items data caching."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        cache_key = "items:all_items"
        
        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.debug("Cache hit for items data")
            return cached_result
        
        # Get fresh data
        result = func(*args, **kwargs)
        
        # Cache for 10 minutes (items data doesn't change often)
        cache.set(cache_key, result, 600)
        logger.debug("Items data cached for 10 minutes")
        
        return result
    return wrapper


def cache_build_optimization(func):
    """Decorator for build optimization caching."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from god, role, and other parameters
        god = kwargs.get('god', args[0] if args else '')
        role = kwargs.get('role', args[1] if len(args) > 1 else '')
        enemy_comp = kwargs.get('enemy_comp', args[2] if len(args) > 2 else [])
        
        cache_key = f"build_opt:{god}:{role}:{hash(str(enemy_comp))}"
        
        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Cache hit for build optimization: {god} {role}")
            return cached_result
        
        # Get fresh optimization
        result = func(*args, **kwargs)
        
        # Cache for 5 minutes (builds can change with meta updates)
        cache.set(cache_key, result, 300)
        logger.debug(f"Build optimization cached: {god} {role}")
        
        return result
    return wrapper


def invalidate_cache_on_update(pattern: str):
    """Decorator to invalidate cache when data is updated."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Clear cache pattern after successful update
            if result:
                cleared_count = cache.clear_pattern(pattern)
                logger.info(f"Invalidated {cleared_count} cache entries for pattern: {pattern}")
            
            return result
        return wrapper
    return decorator


# Flask-specific cache utilities
def init_cache_with_flask(app):
    """Initialize cache with Flask application context."""
    global cache
    
    redis_url = app.config.get('REDIS_URL')
    default_timeout = app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
    
    cache = RedisCache(redis_url, default_timeout)
    
    # Add cache to Flask app
    app.cache = cache
    
    logger.info("✅ Flask cache integration initialized")


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    if not cache.enabled or not cache.redis_client:
        return {"status": "disabled", "reason": "Redis not available"}
    
    try:
        info = cache.redis_client.info()
        return {
            "status": "enabled",
            "connected_clients": info.get("connected_clients", 0),
            "used_memory": info.get("used_memory_human", "0B"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "hit_rate": (
                info.get("keyspace_hits", 0) / 
                max(1, info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0))
            ) * 100
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


# Usage Examples:
"""
# In your database adapter:
from redis_cache import cache_gods_data, cache_items_data

@cache_gods_data
def get_all_gods(self):
    # Your existing code
    pass

@cache_items_data  
def get_all_items(self):
    # Your existing code
    pass

# In your build optimizer:
from redis_cache import cache_build_optimization

@cache_build_optimization
def optimize_build(self, god, role, enemy_comp=None):
    # Your existing code
    pass

# In your Flask app:
from redis_cache import init_cache_with_flask

init_cache_with_flask(app)
""" 