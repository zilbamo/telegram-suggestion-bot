"""CallbackData factories для inline-кнопок."""

from aiogram.filters.callback_data import CallbackData


class SubmissionAction(CallbackData, prefix="sub"):
    """Callback для кнопок под заявкой.
    
    Attributes:
        action: Действие (take, delete, ban, reply)
        user_id: ID пользователя-автора заявки
    """
    action: str
    user_id: int


class BroadcastAction(CallbackData, prefix="bc"):
    """Callback для кнопок подтверждения рассылки.
    
    Attributes:
        action: Действие (send, cancel)
    """
    action: str
