"""Inline-клавиатуры для админ-панели."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .callbacks import AdminAction


def get_admin_menu_kb() -> InlineKeyboardMarkup:
    """Главное меню админ-панели."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📊 Статистика", callback_data=AdminAction(action="stats"))
    builder.button(text="📢 Рассылка", callback_data=AdminAction(action="broadcast"))
    builder.button(text="🔓 Разбан", callback_data=AdminAction(action="unban"))
    builder.button(text="👥 Админы", callback_data=AdminAction(action="admins"))
    
    builder.adjust(2, 2)
    return builder.as_markup()


def get_back_to_admin_kb() -> InlineKeyboardMarkup:
    """Кнопка возврата в админ-меню."""
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ Назад", callback_data=AdminAction(action="menu"))
    return builder.as_markup()


def get_cancel_kb() -> InlineKeyboardMarkup:
    """Кнопка отмены действия."""
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data=AdminAction(action="cancel"))
    return builder.as_markup()
