"""
Multi-layer caching strategy: Memory → Redis → Database
"""

import hashlib
import json
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CacheStrategy:
    """Hierarchical caching with fallback"""
    
    def __init__(self, redis_client=None, enable_memory=True, enable_redis=True):
        self.redis_client = redis_client
        self.enable_memory = enable_memory
        self.enable_redis = enable_redis
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.memory_cache_hits = 0
        self.memory_cache_misses = 0
        self.redis_hits = 0
        self.redis_misses = 0
    
    @staticmethod
    def _generate_key(prompt: str) -> str:
        """Generate cache key from prompt"""
        return f"prompt:{hashlib.sha256(prompt.encode()).hexdigest()}"
    
    @staticmethod
    def _is_expired(entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired"""
        created_at = datetime.fromisoformat(entry["created_at"])
        ttl = entry.get("ttl", 3600)
        return (datetime.now() - created_at).total_seconds() > ttl
    
    # ==========================================
    # LAYER 1: Memory Cache (Fastest)
    # ==========================================
    async def get_from_memory(self, prompt: str) -> Optional[Dict]:
        """Get from in-memory cache"""
        
        if not self.enable_memory:
            return None
        
        cache_key = self._generate_key(prompt)
        
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            
            if not self._is_expired(entry):
                self.memory_cache_hits += 1
                logger.debug(f"Memory cache hit: {cache_key[:20]}...")
                return entry["result"]
            else:
                # Clean up expired entry
                del self.memory_cache[cache_key]
        
        self.memory_cache_misses += 1
        return None
    
    async def set_memory_cache(
        self,
        prompt: str,
        result: Dict,
        ttl: int = 3600
    ):
        """Store in memory cache"""
        
        if not self.enable_memory:
            return
        
        cache_key = self._generate_key(prompt)
        self.memory_cache[cache_key] = {
            "result": result,
            "created_at": datetime.now().isoformat(),
            "ttl": ttl,
            "hits": 0
        }
    
    # ==========================================
    # LAYER 2: Redis Cache (Distributed)
    # ==========================================
    async def get_from_redis(self, prompt: str) -> Optional[Dict]:
        """Get from Redis cache"""
        
        if not self.enable_redis or not self.redis_client:
            return None
        
        cache_key = self._generate_key(prompt)
        
        try:
            result = await self.redis_client.get(cache_key)
            
            if result:
                self.redis_hits += 1
                logger.debug(f"Redis cache hit: {cache_key[:20]}...")
                return json.loads(result)
            
            self.redis_misses += 1
            return None
            
        except Exception as e:
            logger.error(f"Redis read error: {e}")
            return None
    
    async def set_redis_cache(
        self,
        prompt: str,
        result: Dict,
        ttl: int = 3600
    ):
        """Store in Redis cache"""
        
        if not self.enable_redis or not self.redis_client:
            return
        
        cache_key = self._generate_key(prompt)
        
        try:
            await self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result)
            )
            logger.debug(f"Stored in Redis: {cache_key[:20]}...")
            
        except Exception as e:
            logger.error(f"Redis write error: {e}")
    
    # ==========================================
    # MAIN: Get with fallback
    # ==========================================
    async def get(self, prompt: str) -> Optional[Dict]:
        """Try to get from cache (memory → redis)"""
        
        # Try memory first
        result = await self.get_from_memory(prompt)
        if result:
            return result
        
        # Try Redis next
        result = await self.get_from_redis(prompt)
        if result:
            # Populate memory cache from Redis
            await self.set_memory_cache(prompt, result)
            return result
        
        return None
    
    async def set(
        self,
        prompt: str,
        result: Dict,
        ttl: int = 3600,
        memory_only: bool = False
    ):
        """Store in cache (memory + redis)"""
        
        await self.set_memory_cache(prompt, result, ttl)
        
        if not memory_only:
            await self.set_redis_cache(prompt, result, ttl)
    
    # ==========================================
    # Metrics
    # ==========================================
    def get_hit_ratio(self) -> Dict[str, float]:
        """Calculate cache hit ratios"""
        
        memory_total = self.memory_cache_hits + self.memory_cache_misses
        redis_total = self.redis_hits + self.redis_misses
        
        return {
            "memory_hit_ratio": (
                self.memory_cache_hits / memory_total
                if memory_total > 0 else 0.0
            ),
            "redis_hit_ratio": (
                self.redis_hits / redis_total
                if redis_total > 0 else 0.0
            ),
            "memory_hits": self.memory_cache_hits,
            "memory_misses": self.memory_cache_misses,
            "redis_hits": self.redis_hits,
            "redis_misses": self.redis_misses,
        }
    
    def clear(self):
        """Clear all caches"""
        self.memory_cache.clear()
        self.memory_cache_hits = 0
        self.memory_cache_misses = 0


class RequestDeduplicator:
    """
    In-flight request deduplication:
    If 2 identical requests arrive within 100ms, return same result
    """
    
    def __init__(self):
        self.in_flight: Dict[str, asyncio.Future] = {}
        self.dedup_window_ms = 100
    
    async def execute_once(
        self,
        prompt: str,
        analyzer
    ) -> Dict:
        """
        If request in progress, wait for it.
        Otherwise, execute and cache the future.
        """
        
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
        
        if prompt_hash in self.in_flight:
            logger.debug(f"Request dedup hit: {prompt_hash[:20]}...")
            try:
                return await asyncio.wait_for(
                    self.in_flight[prompt_hash],
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                logger.error(f"In-flight request timeout: {prompt_hash[:20]}...")
                del self.in_flight[prompt_hash]
        
        # Start new request
        logger.debug(f"New in-flight request: {prompt_hash[:20]}...")
        future = asyncio.create_task(analyzer.analyze_async(prompt))
        self.in_flight[prompt_hash] = future
        
        try:
            result = await future
            return result
        finally:
            # Remove from in-flight after deduplication window
            await asyncio.sleep(self.dedup_window_ms / 1000.0)
            if prompt_hash in self.in_flight:
                del self.in_flight[prompt_hash]
