"""Inline-клавиатуры для бота."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .callbacks import SubmissionAction, BroadcastAction


def get_submission_kb(
    user_id: int,
    first_msg_id: int = 0,
    last_msg_id: int = 0
) -> InlineKeyboardMarkup:
    """Клавиатура под заявкой в админ-группе.
    
    Args:
        user_id: ID пользователя-автора заявки
        first_msg_id: ID первого сообщения альбома (0 если не альбом)
        last_msg_id: ID последнего сообщения альбома (0 если не альбом)
        
    Returns:
        Клавиатура с 4 кнопками: Взял, Удалить, БАН, Ответить
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="👁 Взял",
        callback_data=SubmissionAction(
            action="take", user_id=user_id,
            first_msg_id=first_msg_id, last_msg_id=last_msg_id
        )
    )
    builder.button(
        text="🗑 Удалить",
        callback_data=SubmissionAction(
            action="delete", user_id=user_id,
            first_msg_id=first_msg_id, last_msg_id=last_msg_id
        )
    )
    builder.button(
        text="🚫 БАН",
        callback_data=SubmissionAction(
            action="ban", user_id=user_id,
            first_msg_id=first_msg_id, last_msg_id=last_msg_id
        )
    )
    builder.button(
        text="↩️ Ответить",
        callback_data=SubmissionAction(
            action="reply", user_id=user_id,
            first_msg_id=first_msg_id, last_msg_id=last_msg_id
        )
    )
    
    builder.adjust(2, 2)  # 2 кнопки в ряд
    
    return builder.as_markup()


def get_broadcast_confirm_kb() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения рассылки.
    
    Returns:
        Клавиатура с 2 кнопками: Отправить, Отмена
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="🚀 Отправить",
        callback_data=BroadcastAction(action="send")
    )
    builder.button(
        text="❌ Отмена",
        callback_data=BroadcastAction(action="cancel")
    )
    
    builder.adjust(2)  # 2 кнопки в ряд
    
    return builder.as_markup()
