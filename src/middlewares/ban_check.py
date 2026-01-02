"""Ban check middleware - blocks processing for banned users."""

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

from src.database.requests import is_user_banned


class BanCheckMiddleware(BaseMiddleware):
    """
    Middleware that checks if user is banned before processing.
    
    If user has is_banned=True in database, the message is silently ignored
    (no response, no forwarding, no further processing).
    
    Requirements: 3.1, 3.3
    """

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id if event.from_user else None
        
        if user_id is None:
            return None
        
        if await is_user_banned(user_id):
            # Silently ignore banned users - no response, no processing
            return None
        
        return await handler(event, data)
