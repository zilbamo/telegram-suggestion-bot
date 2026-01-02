import logging
from aiogram import Router
from aiogram.types import ErrorEvent

router = Router(name="errors")
logger = logging.getLogger(__name__)


@router.error()
async def global_error_handler(event: ErrorEvent) -> bool:
    """
    Глобальный обработчик ошибок.
    Логирует все необработанные исключения.
    """
    logger.exception(
        "Необработанное исключение при обработке update %s: %s",
        event.update.update_id if event.update else "unknown",
        event.exception,
    )
    return True
