"""Helper utilities для форматирования и экранирования."""

import html


def escape_html(text: str) -> str:
    """Экранирует HTML-спецсимволы в тексте.
    
    Args:
        text: Исходный текст с возможными HTML-символами.
        
    Returns:
        Текст с экранированными символами (<, >, &, ", ').
    """
    return html.escape(text, quote=True)


def format_submission_caption(
    user_id: int,
    full_name: str,
    username: str | None = None
) -> str:
    """Форматирует метаданные заявки для админ-группы.
    
    Args:
        user_id: ID пользователя Telegram.
        full_name: Полное имя пользователя.
        username: Username пользователя (может быть None).
        
    Returns:
        Отформатированная строка вида:
        #id_123456
        От: Иван Иванов (@username)
    """
    safe_name = escape_html(full_name)
    
    if username:
        safe_username = escape_html(username)
        user_info = f"От: {safe_name} (@{safe_username})"
    else:
        user_info = f"От: {safe_name}"
    
    return f"#id_{user_id}\n{user_info}"
