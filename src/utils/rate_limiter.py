"""Rate limiting utilities."""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict
import structlog

logger = structlog.get_logger(__name__)


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(
        self,
        rate: int,
        per: int = 60,
        burst: Optional[int] = None
    ):
        """Initialize rate limiter.
        
        Args:
            rate: Number of allowed actions
            per: Time period in seconds
            burst: Maximum burst size (default = rate)
        """
        self.rate = rate
        self.per = per
        self.burst = burst or rate
        self._buckets: Dict[str, Dict] = defaultdict(lambda: {
            "tokens": self.burst,
            "last_update": datetime.utcnow()
        })
        self._lock = asyncio.Lock()
    
    async def acquire(
        self,
        key: str = "default",
        tokens: int = 1,
        wait: bool = True
    ) -> bool:
        """Acquire tokens from the bucket.
        
        Args:
            key: Bucket key for different rate limits
            tokens: Number of tokens to acquire
            wait: Whether to wait if not enough tokens
            
        Returns:
            True if tokens acquired, False otherwise
        """
        async with self._lock:
            bucket = self._buckets[key]
            now = datetime.utcnow()
            
            # Calculate tokens to add since last update
            elapsed = (now - bucket["last_update"]).total_seconds()
            tokens_to_add = elapsed * (self.rate / self.per)
            bucket["tokens"] = min(self.burst, bucket["tokens"] + tokens_to_add)
            bucket["last_update"] = now
            
            if bucket["tokens"] >= tokens:
                bucket["tokens"] -= tokens
                return True
            
            if wait:
                # Calculate wait time
                tokens_needed = tokens - bucket["tokens"]
                wait_time = tokens_needed * (self.per / self.rate)
                
                logger.debug(f"Rate limit: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                
                bucket["tokens"] = 0
                bucket["last_update"] = datetime.utcnow()
                return True
            
            return False
    
    async def check(
        self,
        key: str = "default",
        tokens: int = 1
    ) -> tuple[bool, float]:
        """Check if tokens are available without consuming.
        
        Args:
            key: Bucket key
            tokens: Number of tokens to check
            
        Returns:
            Tuple of (available, wait_time_if_not)
        """
        async with self._lock:
            bucket = self._buckets[key]
            now = datetime.utcnow()
            
            # Calculate current tokens
            elapsed = (now - bucket["last_update"]).total_seconds()
            current_tokens = min(
                self.burst,
                bucket["tokens"] + elapsed * (self.rate / self.per)
            )
            
            if current_tokens >= tokens:
                return True, 0.0
            
            tokens_needed = tokens - current_tokens
            wait_time = tokens_needed * (self.per / self.rate)
            return False, wait_time
    
    def reset(self, key: str = "default") -> None:
        """Reset a bucket to full.
        
        Args:
            key: Bucket key to reset
        """
        self._buckets[key] = {
            "tokens": self.burst,
            "last_update": datetime.utcnow()
        }
    
    def get_stats(self, key: str = "default") -> Dict:
        """Get current bucket stats.
        
        Args:
            key: Bucket key
            
        Returns:
            Stats dictionary
        """
        bucket = self._buckets[key]
        now = datetime.utcnow()
        elapsed = (now - bucket["last_update"]).total_seconds()
        current_tokens = min(
            self.burst,
            bucket["tokens"] + elapsed * (self.rate / self.per)
        )
        
        return {
            "tokens_available": round(current_tokens, 2),
            "max_tokens": self.burst,
            "rate": f"{self.rate}/{self.per}s",
            "last_update": bucket["last_update"].isoformat()
        }


# Pre-configured limiters
message_limiter = RateLimiter(rate=3, per=60)  # 3 messages per minute
group_join_limiter = RateLimiter(rate=5, per=86400)  # 5 joins per day
dm_limiter = RateLimiter(rate=10, per=3600)  # 10 DMs per hour
