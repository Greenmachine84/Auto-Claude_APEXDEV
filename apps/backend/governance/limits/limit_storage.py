"""
Limit Storage - Phase 9 Implementation.

Persistent storage for rate limits and quotas.

World-Class Standards:
- Multiple backends
- Atomic operations
- Data persistence
"""

from typing import Dict, List, Optional, Any, Protocol
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import json
import threading
import logging
from pathlib import Path

from ..models import RateLimit, Quota, QuotaUsage, SUPPORTED_PROVIDERS


logger = logging.getLogger(__name__)


class StorageBackend(Protocol):
    """Protocol for storage backends."""
    
    def get(self, key: str) -> Optional[str]: ...
    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool: ...
    def delete(self, key: str) -> bool: ...
    def exists(self, key: str) -> bool: ...
    def keys(self, pattern: str) -> List[str]: ...


class InMemoryStorage:
    """
    In-memory storage backend.
    Thread-safe implementation.
    """
    
    def __init__(self) -> None:
        self._data: Dict[str, tuple[str, Optional[datetime]]] = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        with self._lock:
            if key not in self._data:
                return None
            
            value, expiry = self._data[key]
            if expiry and datetime.utcnow() > expiry:
                del self._data[key]
                return None
            
            return value
    
    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set value with optional TTL in seconds."""
        with self._lock:
            expiry = None
            if ttl:
                expiry = datetime.utcnow() + timedelta(seconds=ttl)
            
            self._data[key] = (value, expiry)
            return True
    
    def delete(self, key: str) -> bool:
        """Delete key."""
        with self._lock:
            if key in self._data:
                del self._data[key]
                return True
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        return self.get(key) is not None
    
    def keys(self, pattern: str) -> List[str]:
        """Get keys matching pattern (simple prefix match)."""
        with self._lock:
            prefix = pattern.rstrip("*")
            return [k for k in self._data.keys() if k.startswith(prefix)]
    
    def cleanup_expired(self) -> int:
        """Remove expired entries."""
        count = 0
        with self._lock:
            now = datetime.utcnow()
            expired = [
                k for k, (_, expiry) in self._data.items()
                if expiry and now > expiry
            ]
            for key in expired:
                del self._data[key]
                count += 1
        return count


class FileStorage:
    """
    File-based storage backend.
    """
    
    def __init__(self, storage_path: str) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
    
    def _key_to_path(self, key: str) -> Path:
        """Convert key to file path."""
        safe_key = key.replace(":", "_").replace("/", "_")
        return self.storage_path / f"{safe_key}.json"
    
    def get(self, key: str) -> Optional[str]:
        """Get value from file."""
        path = self._key_to_path(key)
        
        with self._lock:
            if not path.exists():
                return None
            
            try:
                data = json.loads(path.read_text())
                expiry = data.get("expiry")
                if expiry:
                    expiry_dt = datetime.fromisoformat(expiry)
                    if datetime.utcnow() > expiry_dt:
                        path.unlink()
                        return None
                
                return data.get("value")
            except Exception as e:
                logger.error(f"Error reading {path}: {e}")
                return None
    
    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Write value to file."""
        path = self._key_to_path(key)
        
        with self._lock:
            try:
                data = {"value": value}
                if ttl:
                    expiry = datetime.utcnow() + timedelta(seconds=ttl)
                    data["expiry"] = expiry.isoformat()
                
                path.write_text(json.dumps(data))
                return True
            except Exception as e:
                logger.error(f"Error writing {path}: {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """Delete file."""
        path = self._key_to_path(key)
        
        with self._lock:
            if path.exists():
                path.unlink()
                return True
            return False
    
    def exists(self, key: str) -> bool:
        """Check if file exists."""
        return self.get(key) is not None
    
    def keys(self, pattern: str) -> List[str]:
        """Get keys matching pattern."""
        prefix = pattern.rstrip("*").replace(":", "_").replace("/", "_")
        keys = []
        
        with self._lock:
            for path in self.storage_path.glob(f"{prefix}*.json"):
                key = path.stem.replace("_", ":")
                keys.append(key)
        
        return keys


class LimitStorage:
    """
    Storage manager for rate limits and quotas.
    """
    
    def __init__(
        self,
        backend: Optional[StorageBackend] = None
    ) -> None:
        self._backend = backend or InMemoryStorage()
        self._prefix = "governance:limits:"
    
    def _make_key(self, *parts: str) -> str:
        """Create storage key."""
        return self._prefix + ":".join(parts)
    
    # Rate limit storage
    def save_rate_limit_usage(
        self,
        provider: str,
        user_id: str,
        count: int,
        tokens: int,
        window_seconds: int
    ) -> bool:
        """Save rate limit usage."""
        key = self._make_key("rate", provider, user_id)
        data = json.dumps({
            "count": count,
            "tokens": tokens,
            "timestamp": datetime.utcnow().isoformat(),
        })
        return self._backend.set(key, data, ttl=window_seconds)
    
    def get_rate_limit_usage(
        self,
        provider: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get rate limit usage."""
        key = self._make_key("rate", provider, user_id)
        data = self._backend.get(key)
        if data:
            return json.loads(data)
        return None
    
    # Quota storage
    def save_quota_usage(
        self,
        provider: str,
        user_id: str,
        usage: QuotaUsage
    ) -> bool:
        """Save quota usage."""
        key = self._make_key("quota", provider, user_id)
        data = json.dumps({
            "current_usage": usage.current_usage,
            "limit": usage.limit,
            "period_start": usage.period_start.isoformat(),
            "period_end": usage.period_end.isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
        })
        # Keep for rest of period
        ttl = int((usage.period_end - datetime.utcnow()).total_seconds())
        return self._backend.set(key, data, ttl=max(ttl, 60))
    
    def get_quota_usage(
        self,
        provider: str,
        user_id: str
    ) -> Optional[QuotaUsage]:
        """Get quota usage."""
        key = self._make_key("quota", provider, user_id)
        data = self._backend.get(key)
        if not data:
            return None
        
        parsed = json.loads(data)
        return QuotaUsage(
            provider=provider,
            user_id=user_id,
            current_usage=parsed["current_usage"],
            limit=parsed["limit"],
            period_start=datetime.fromisoformat(parsed["period_start"]),
            period_end=datetime.fromisoformat(parsed["period_end"]),
            unit="USD",
        )
    
    # Throttle state storage
    def save_throttle_state(
        self,
        provider: str,
        state: str,
        backoff: float
    ) -> bool:
        """Save throttle state."""
        key = self._make_key("throttle", provider)
        data = json.dumps({
            "state": state,
            "backoff": backoff,
            "timestamp": datetime.utcnow().isoformat(),
        })
        return self._backend.set(key, data, ttl=3600)  # 1 hour
    
    def get_throttle_state(self, provider: str) -> Optional[Dict[str, Any]]:
        """Get throttle state."""
        key = self._make_key("throttle", provider)
        data = self._backend.get(key)
        if data:
            return json.loads(data)
        return None
    
    # Bulk operations
    def get_all_quota_usage(self) -> Dict[str, Dict[str, QuotaUsage]]:
        """Get all quota usage."""
        result: Dict[str, Dict[str, QuotaUsage]] = {}
        
        for provider in SUPPORTED_PROVIDERS:
            result[provider] = {}
            keys = self._backend.keys(self._make_key("quota", provider, "*"))
            for key in keys:
                parts = key.split(":")
                if len(parts) >= 4:
                    user_id = parts[-1]
                    usage = self.get_quota_usage(provider, user_id)
                    if usage:
                        result[provider][user_id] = usage
        
        return result
    
    def clear_provider(self, provider: str) -> int:
        """Clear all data for provider."""
        count = 0
        for prefix in ["rate", "quota", "throttle"]:
            keys = self._backend.keys(self._make_key(prefix, provider, "*"))
            for key in keys:
                if self._backend.delete(key):
                    count += 1
        return count
