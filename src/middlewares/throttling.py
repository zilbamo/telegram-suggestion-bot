"""Throttling middleware - limits message rate per user."""

import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware that limits message rate to 1 message per 3 seconds per user.
    
    Uses in-memory dict with timestamps. Excess messages are silently ignored
    (no response sent to user).
    
    Includes periodic cleanup of stale entries to prevent memory leaks.
    
    Requirements: 3.2
    """

    def __init__(
        self, 
        rate_limit: float = 3.0,
        cleanup_interval: float = 300.0,  # 5 minutes
        max_age: float = 600.0,  # 10 minutes
    ) -> None:
        """
        Initialize throttling middleware.
        
        Args:
            rate_limit: Minimum seconds between messages (default: 3.0)
            cleanup_interval: How often to run cleanup (default: 300s)
            max_age: Remove entries older than this (default: 600s)
        """
        self.rate_limit = rate_limit
        self.cleanup_interval = cleanup_interval
        self.max_age = max_age
        self.user_timestamps: dict[int, float] = {}
        self.last_cleanup: float = 0.0

    def _cleanup_stale_entries(self, current_time: float) -> None:
        """Remove entries older than max_age."""
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        self.last_cleanup = current_time
        cutoff = current_time - self.max_age
        
        # Create new dict with only fresh entries
        self.user_timestamps = {
            uid: ts for uid, ts in self.user_timestamps.items()
            if ts > cutoff
        }

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id if event.from_user else None
        
        if user_id is None:
            return None
        
        current_time = time.monotonic()
        
        # Periodic cleanup
        self._cleanup_stale_entries(current_time)
        
        last_time = self.user_timestamps.get(user_id, 0.0)
        
        if current_time - last_time < self.rate_limit:
            # Rate limit exceeded - silently ignore
            return None
        
        # Update timestamp and process message
        self.user_timestamps[user_id] = current_time
        
        return await handler(event, data)
