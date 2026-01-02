"""Album middleware - collects MediaGroup items into a single list.

Based on aiogram_album patterns with TTL cache and proper locking.
"""

import asyncio
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message


class AlbumMiddleware(BaseMiddleware):
    """
    Middleware that collects MediaGroup (album) messages into a single list.
    
    Uses proper locking pattern: lock is acquired BEFORE adding to collection,
    and only the first coroutine to acquire the lock processes the album.
    
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
        self.processing: set[str] = set()  # Track albums being processed

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
        
        lock = self.locks[media_group_id]
        
        # Try to be the first to process this album
        is_first = False
        async with lock:
            # Check if already being processed
            if media_group_id in self.processing:
                # Another coroutine is handling this album, just add message
                if media_group_id in self.albums:
                    self.albums[media_group_id].append(event)
                return None
            
            # We're first - mark as processing and init collection
            self.processing.add(media_group_id)
            self.albums[media_group_id] = [event]
            is_first = True
        
        if not is_first:
            return None
        
        # Wait for all album items to arrive
        await asyncio.sleep(self.latency)
        
        # Collect and cleanup atomically
        async with lock:
            album = self.albums.pop(media_group_id, [])
            self.processing.discard(media_group_id)
            self.locks.pop(media_group_id, None)
        
        if not album:
            return None
        
        # Sort by message_id to maintain order
        album.sort(key=lambda m: m.message_id)
        
        # Pass album to handler via data dict
        data["album"] = album
        
        # Use first message as the event
        return await handler(album[0], data)
