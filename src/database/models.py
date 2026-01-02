"""Database models for the suggestion bot."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    """User model representing a bot user in the database."""

    user_id: int
    username: str | None
    full_name: str
    is_banned: bool = False
    is_active: bool = True
    joined_date: datetime = field(default_factory=datetime.now)
