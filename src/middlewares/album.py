"""Album middleware - collects MediaGroup items into a single list."""

import asyncio
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message


class AlbumMiddleware(BaseMiddleware):
    """
    Middleware that collects MediaGroup (album) messages into a single list.
    
    Requirements: 2.9
    """

    def __init__(self, latency: float = 1.0) -> None:
        self.latency = latency
        self.albums: dict[str, list[Message]] = {}
        self.locks: dict[str, asyncio.Lock] = {}

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        if event.media_group_id is None:
            return await handler(event, data)
        
        media_group_id = event.media_group_id
        
        # Get or create lock for this album
        if media_group_id not in self.locks:
            self.locks[media_group_id] = asyncio.Lock()
        lock = self.locks[media_group_id]
        
        # Add message to album collection
        async with lock:
            if media_group_id not in self.albums:
                # First message - create album and schedule processing
                self.albums[media_group_id] = [event]
                is_first = True
            else:
                # Not first - just add to existing album
                self.albums[media_group_id].append(event)
                is_first = False
        
        if not is_first:
            # Not the first message - just return, first one will handle all
            return None
        
        # First message waits for others to arrive
        await asyncio.sleep(self.latency)
        
        # Collect album and cleanup
        async with lock:
            album = self.albums.pop(media_group_id, [])
        
        # Cleanup lock (safe to do outside lock)
        self.locks.pop(media_group_id, None)
        
        if not album:
            return None
        
        # Sort by message_id to maintain order
        album.sort(key=lambda m: m.message_id)
        
        # Pass album to handler
        data["album"] = album
        
        return await handler(album[0], data)
