"""Entry point для Telegram-бота «Предложка»."""

import asyncio
import logging
from logging.handlers import RotatingFileHandler
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from src.config import config
from src.database.requests import init_db
from src.handlers import user_router, admin_router, errors_router
from src.middlewares import BanCheckMiddleware, ThrottlingMiddleware, AlbumMiddleware


def setup_logging() -> None:
    """
    Настройка логирования: вывод в консоль и файл bot.log.
    Формат: время, уровень, сообщение.
    
    Requirements: 10.2
    """
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Консольный handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))

    # Файловый handler с ротацией (макс 100KB, 3 бэкапа)
    file_handler = RotatingFileHandler(
        "bot.log",
        maxBytes=100 * 1024,  # ~1000 строк ≈ 100KB
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


async def main() -> None:
    """
    Главная функция запуска бота.
    
    - Инициализация Bot, Dispatcher
    - Подключение роутеров через dp.include_router()
    - Регистрация middlewares
    - Вызов init_db() при старте
    - dp.start_polling()
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Инициализация бота...")
    
    # Инициализация БД
    await init_db()
    logger.info("База данных инициализирована")
    
    # Создание Bot с дефолтным parse_mode
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Создание Dispatcher с MemoryStorage для FSM
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрация middlewares на message
    # Порядок важен: сначала ban_check, потом throttling, потом album
    dp.message.middleware(BanCheckMiddleware())
    dp.message.middleware(ThrottlingMiddleware(rate_limit=3.0))
    dp.message.middleware(AlbumMiddleware(latency=0.5))
    
    # Подключение роутеров
    # errors_router первым для перехвата ошибок
    dp.include_router(errors_router)
    dp.include_router(admin_router)
    dp.include_router(user_router)
    
    logger.info("Роутеры и middlewares подключены")
    logger.info("Запуск polling...")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
