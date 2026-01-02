import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    bot_token: str
    admin_group_id: int
    admin_ids: list[int]
    db_path: str = "bot.db"

    @classmethod
    def from_env(cls) -> "Config":
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            raise ValueError("BOT_TOKEN is required")

        admin_group_id_str = os.getenv("ADMIN_GROUP_ID")
        if not admin_group_id_str:
            raise ValueError("ADMIN_GROUP_ID is required")

        admin_ids_str = os.getenv("ADMIN_IDS", "")
        admin_ids = [
            int(x.strip()) for x in admin_ids_str.split(",") if x.strip()
        ]

        db_path = os.getenv("DB_PATH", "bot.db")

        return cls(
            bot_token=bot_token,
            admin_group_id=int(admin_group_id_str),
            admin_ids=admin_ids,
            db_path=db_path,
        )


config = Config.from_env()
