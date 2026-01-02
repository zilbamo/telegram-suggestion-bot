"""Database CRUD operations using aiosqlite with parameterized queries."""

from datetime import datetime

import aiosqlite

from src.config import config
from src.database.models import User

DB_PATH = config.db_path


async def init_db() -> None:
    """Create users table if it doesn't exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT NOT NULL,
                is_banned INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                joined_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def add_user(user_id: int, username: str | None, full_name: str) -> None:
    """Add user or ignore if already exists (INSERT OR IGNORE)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO users (user_id, username, full_name)
            VALUES (?, ?, ?)
            """,
            (user_id, username, full_name),
        )
        await db.commit()


async def get_user(user_id: int) -> User | None:
    """Get user by ID, returns None if not found."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return User(
            user_id=row["user_id"],
            username=row["username"],
            full_name=row["full_name"],
            is_banned=bool(row["is_banned"]),
            is_active=bool(row["is_active"]),
            joined_date=datetime.fromisoformat(row["joined_date"]),
        )



async def is_user_banned(user_id: int) -> bool:
    """Check if user is banned. Returns False if user not found."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT is_banned FROM users WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
        if row is None:
            return False
        return bool(row[0])


async def ban_user(user_id: int) -> None:
    """Set is_banned=True for user."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET is_banned = 1 WHERE user_id = ?",
            (user_id,),
        )
        await db.commit()


async def set_user_inactive(user_id: int) -> None:
    """Set is_active=False for user (when bot is blocked)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET is_active = 0 WHERE user_id = ?",
            (user_id,),
        )
        await db.commit()


async def get_active_users() -> list[User]:
    """Get all users where is_banned=False AND is_active=True (for broadcast)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE is_banned = 0 AND is_active = 1"
        )
        rows = await cursor.fetchall()
        return [
            User(
                user_id=row["user_id"],
                username=row["username"],
                full_name=row["full_name"],
                is_banned=bool(row["is_banned"]),
                is_active=bool(row["is_active"]),
                joined_date=datetime.fromisoformat(row["joined_date"]),
            )
            for row in rows
        ]


async def get_stats() -> dict:
    """Get user statistics for admin panel."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Total users
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        total = (await cursor.fetchone())[0]
        
        # Active users
        cursor = await db.execute(
            "SELECT COUNT(*) FROM users WHERE is_active = 1 AND is_banned = 0"
        )
        active = (await cursor.fetchone())[0]
        
        # Banned users
        cursor = await db.execute("SELECT COUNT(*) FROM users WHERE is_banned = 1")
        banned = (await cursor.fetchone())[0]
        
        # Inactive users (blocked bot)
        cursor = await db.execute(
            "SELECT COUNT(*) FROM users WHERE is_active = 0 AND is_banned = 0"
        )
        inactive = (await cursor.fetchone())[0]
        
        return {
            "total": total,
            "active": active,
            "banned": banned,
            "inactive": inactive,
        }


async def unban_user(user_id: int) -> bool:
    """Unban user by ID. Returns True if user was found and unbanned."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT is_banned FROM users WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
        if row is None:
            return False
        
        await db.execute(
            "UPDATE users SET is_banned = 0 WHERE user_id = ?",
            (user_id,),
        )
        await db.commit()
        return True
