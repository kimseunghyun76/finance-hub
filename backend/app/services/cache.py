"""Simple in-memory cache for frequently accessed data"""
from typing import Any, Optional
from datetime import datetime, timedelta
from threading import Lock


class SimpleCache:
    """Thread-safe in-memory cache with TTL support"""

    def __init__(self):
        self._cache = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        with self._lock:
            if key in self._cache:
                value, expires_at = self._cache[key]
                if datetime.utcnow() < expires_at:
                    return value
                else:
                    # Remove expired entry
                    del self._cache[key]
            return None

    def set(self, key: str, value: Any, ttl_seconds: int):
        """Set value in cache with TTL"""
        with self._lock:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            self._cache[key] = (value, expires_at)

    def delete(self, key: str):
        """Delete value from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]

    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()

    def cleanup_expired(self):
        """Remove all expired entries"""
        with self._lock:
            current_time = datetime.utcnow()
            expired_keys = [
                key for key, (_, expires_at) in self._cache.items()
                if current_time >= expires_at
            ]
            for key in expired_keys:
                del self._cache[key]
            return len(expired_keys)

    def get_stats(self):
        """Get cache statistics"""
        with self._lock:
            current_time = datetime.utcnow()
            active = sum(1 for _, expires_at in self._cache.values() if current_time < expires_at)
            expired = sum(1 for _, expires_at in self._cache.values() if current_time >= expires_at)

            return {
                "total_entries": len(self._cache),
                "active_entries": active,
                "expired_entries": expired,
            }


class RateLimitCircuitBreaker:
    """Circuit breaker for handling API rate limits"""

    def __init__(self, cooldown_seconds: int = 300):
        """
        Initialize circuit breaker

        Args:
            cooldown_seconds: Time to wait after rate limit before allowing requests again (default 5 minutes)
        """
        self._is_open = False
        self._cooldown_until = None
        self._lock = Lock()
        self._cooldown_seconds = cooldown_seconds

    def is_open(self) -> bool:
        """Check if circuit breaker is open (blocking requests)"""
        with self._lock:
            if self._is_open and self._cooldown_until:
                # Check if cooldown period has passed
                if datetime.utcnow() >= self._cooldown_until:
                    self._is_open = False
                    self._cooldown_until = None
                    print("✅ Circuit breaker closed - resuming API calls")
            return self._is_open

    def trip(self, reason: str = "Rate limit detected"):
        """Trip the circuit breaker (open it to block requests)"""
        with self._lock:
            if not self._is_open:
                self._is_open = True
                self._cooldown_until = datetime.utcnow() + timedelta(seconds=self._cooldown_seconds)
                print(f"🚨 Circuit breaker opened: {reason}")
                print(f"⏳ Will resume API calls at {self._cooldown_until.strftime('%Y-%m-%d %H:%M:%S')}")

    def reset(self):
        """Manually reset the circuit breaker"""
        with self._lock:
            self._is_open = False
            self._cooldown_until = None
            print("✅ Circuit breaker manually reset")

    def get_status(self):
        """Get circuit breaker status"""
        with self._lock:
            return {
                "is_open": self._is_open,
                "cooldown_until": self._cooldown_until.isoformat() if self._cooldown_until else None,
                "seconds_remaining": max(0, (self._cooldown_until - datetime.utcnow()).total_seconds()) if self._cooldown_until else 0
            }


# Global cache instances
stock_info_cache = SimpleCache()  # Stock info cache (1 hour TTL)
stock_quote_cache = SimpleCache()  # Stock quote cache (5 minutes TTL)
analyst_targets_cache = SimpleCache()  # Analyst targets cache (1 hour TTL)

# Rate limit circuit breaker for Yahoo Finance API
yfinance_circuit_breaker = RateLimitCircuitBreaker(cooldown_seconds=300)  # 5 minute cooldown


# Cache TTL constants (in seconds)
STOCK_INFO_TTL = 3600  # 1 hour
STOCK_QUOTE_TTL = 300  # 5 minutes
ANALYST_TARGETS_TTL = 3600  # 1 hour
