"""CallbackData factories для inline-кнопок."""

from aiogram.filters.callback_data import CallbackData


class SubmissionAction(CallbackData, prefix="sub"):
    """Callback для кнопок под заявкой.
    
    Attributes:
        action: Действие (take, delete, ban, reply)
        user_id: ID пользователя-автора заявки
        first_msg_id: ID первого сообщения альбома (0 если не альбом)
        last_msg_id: ID последнего сообщения альбома (0 если не альбом)
    """
    action: str
    user_id: int
    first_msg_id: int = 0
    last_msg_id: int = 0


class BroadcastAction(CallbackData, prefix="bc"):
    """Callback для кнопок подтверждения рассылки.
    
    Attributes:
        action: Действие (send, cancel)
    """
    action: str
