"""Album middleware - collects MediaGroup items into a single list."""

import asyncio
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message


class AlbumMiddleware(BaseMiddleware):
    """
    Middleware that collects MediaGroup (album) messages into a single list.
    
    When a message with media_group_id is received, waits 0.5 seconds to collect
    all items, then passes them to handler as 'album' in data dict.
    
    For non-album messages, passes through normally without 'album' key.
    
    Requirements: 2.9
    """

    def __init__(self, latency: float = 0.5) -> None:
        """
        Initialize album middleware.
        
        Args:
            latency: Seconds to wait for collecting album items (default: 0.5)
        """
        self.latency = latency
        self.albums: dict[str, list[Message]] = {}
        self.locks: dict[str, asyncio.Lock] = {}

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        # Not a media group - process normally
        if event.media_group_id is None:
            return await handler(event, data)
        
        media_group_id = event.media_group_id
        
        # Create lock for this album if not exists
        if media_group_id not in self.locks:
            self.locks[media_group_id] = asyncio.Lock()
        
        # Add message to album collection
        if media_group_id not in self.albums:
            self.albums[media_group_id] = []
        self.albums[media_group_id].append(event)
        
        # Only first message in group triggers the handler
        async with self.locks[media_group_id]:
            # Check if we're the first to acquire lock for this album
            if len(self.albums.get(media_group_id, [])) == 0:
                # Album already processed by another coroutine
                return None
            
            # Wait for all album items to arrive
            await asyncio.sleep(self.latency)
            
            # Get collected messages and clean up
            album = self.albums.pop(media_group_id, [])
            self.locks.pop(media_group_id, None)
            
            if not album:
                return None
            
            # Sort by message_id to maintain order
            album.sort(key=lambda m: m.message_id)
            
            # Pass album to handler via data dict
            data["album"] = album
            
            # Use first message as the event
            return await handler(album[0], data)
