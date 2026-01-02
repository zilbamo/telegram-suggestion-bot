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
    
    Requirements: 3.2
    """

    def __init__(self, rate_limit: float = 3.0) -> None:
        """
        Initialize throttling middleware.
        
        Args:
            rate_limit: Minimum seconds between messages (default: 3.0)
        """
        self.rate_limit = rate_limit
        self.user_timestamps: dict[int, float] = {}

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
        last_time = self.user_timestamps.get(user_id, 0.0)
        
        if current_time - last_time < self.rate_limit:
            # Rate limit exceeded - silently ignore
            return None
        
        # Update timestamp and process message
        self.user_timestamps[user_id] = current_time
        
        return await handler(event, data)
