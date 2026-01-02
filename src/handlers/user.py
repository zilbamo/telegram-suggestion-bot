"""User handlers - /start и приём контента."""

from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.config import config
from src.database.requests import add_user
from src.keyboards.inline import get_submission_kb
from src.utils.helpers import escape_html, format_submission_caption

router = Router(name="user")

WELCOME_MESSAGE = (
    "Привет! Присылай свои новости, мемы или вопросы. "
    "Я передам их админам анонимно. "
    "Поддерживаю текст, фото, видео и кружочки."
)

SUBMISSION_SENT = "Сообщение отправлено администрации."


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Обработка команды /start - регистрация пользователя.
    
    Requirements: 1.1, 1.2, 1.3
    """
    user = message.from_user
    if not user:
        return
    
    # Регистрация в БД (INSERT OR IGNORE - не создаёт дубликаты)
    await add_user(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
    )
    
    await message.answer(WELCOME_MESSAGE)


@router.message(F.text & ~F.text.startswith("/"))
async def handle_text(message: Message, bot: Bot) -> None:
    """Обработка текстовых сообщений.
    
    Requirements: 2.1, 2.10, 4.1-4.4
    """
    user = message.from_user
    if not user:
        return
    
    caption = format_submission_caption(
        user_id=user.id,
        full_name=user.full_name,
        username=user.username,
    )
    
    # Экранируем текст пользователя
    safe_text = escape_html(message.text or "")
    full_text = f"{caption}\n\n{safe_text}"
    
    await bot.send_message(
        chat_id=config.admin_group_id,
        text=full_text,
        parse_mode="HTML",
        reply_markup=get_submission_kb(user.id),
    )
    
    await message.answer(SUBMISSION_SENT)


@router.message(F.photo, ~F.media_group_id)
async def handle_photo(message: Message, bot: Bot) -> None:
    """Обработка одиночного фото (не альбом).
    
    Requirements: 2.2, 2.10, 4.1-4.4
    """
    
    user = message.from_user
    if not user:
        return
    
    caption = format_submission_caption(
        user_id=user.id,
        full_name=user.full_name,
        username=user.username,
    )
    
    # Добавляем оригинальную подпись если есть
    if message.caption:
        safe_caption = escape_html(message.caption)
        caption = f"{caption}\n\n{safe_caption}"
    
    # Берём фото максимального размера
    photo = message.photo[-1]
    
    await bot.send_photo(
        chat_id=config.admin_group_id,
        photo=photo.file_id,
        caption=caption,
        parse_mode="HTML",
        reply_markup=get_submission_kb(user.id),
    )
    
    await message.answer(SUBMISSION_SENT)


@router.message(F.video, ~F.media_group_id)
async def handle_video(message: Message, bot: Bot) -> None:
    """Обработка одиночного видео (не альбом).
    
    Requirements: 2.3, 2.10, 4.1-4.4
    """
    
    user = message.from_user
    if not user:
        return
    
    caption = format_submission_caption(
        user_id=user.id,
        full_name=user.full_name,
        username=user.username,
    )
    
    if message.caption:
        safe_caption = escape_html(message.caption)
        caption = f"{caption}\n\n{safe_caption}"
    
    await bot.send_video(
        chat_id=config.admin_group_id,
        video=message.video.file_id,
        caption=caption,
        parse_mode="HTML",
        reply_markup=get_submission_kb(user.id),
    )
    
    await message.answer(SUBMISSION_SENT)


@router.message(F.voice)
async def handle_voice(message: Message, bot: Bot) -> None:
    """Обработка голосовых сообщений.
    
    Requirements: 2.4, 2.10, 4.1-4.4
    """
    user = message.from_user
    if not user:
        return
    
    caption = format_submission_caption(
        user_id=user.id,
        full_name=user.full_name,
        username=user.username,
    )
    
    await bot.send_voice(
        chat_id=config.admin_group_id,
        voice=message.voice.file_id,
        caption=caption,
        parse_mode="HTML",
        reply_markup=get_submission_kb(user.id),
    )
    
    await message.answer(SUBMISSION_SENT)


@router.message(F.video_note)
async def handle_video_note(message: Message, bot: Bot) -> None:
    """Обработка кружочков (video_note).
    
    Requirements: 2.5, 2.10, 4.1-4.4
    """
    user = message.from_user
    if not user:
        return
    
    caption = format_submission_caption(
        user_id=user.id,
        full_name=user.full_name,
        username=user.username,
    )
    
    # video_note не поддерживает caption, отправляем текст отдельно
    caption_msg = await bot.send_message(
        chat_id=config.admin_group_id,
        text=caption,
        parse_mode="HTML",
    )
    
    await bot.send_video_note(
        chat_id=config.admin_group_id,
        video_note=message.video_note.file_id,
        reply_markup=get_submission_kb(
            user_id=user.id,
            first_msg_id=caption_msg.message_id,
            last_msg_id=caption_msg.message_id
        ),
    )
    
    await message.answer(SUBMISSION_SENT)


@router.message(F.document, ~F.media_group_id)
async def handle_document(message: Message, bot: Bot) -> None:
    """Обработка одиночного документа (не альбом).
    
    Requirements: 2.6, 2.10, 4.1-4.4
    """
    
    user = message.from_user
    if not user:
        return
    
    caption = format_submission_caption(
        user_id=user.id,
        full_name=user.full_name,
        username=user.username,
    )
    
    if message.caption:
        safe_caption = escape_html(message.caption)
        caption = f"{caption}\n\n{safe_caption}"
    
    await bot.send_document(
        chat_id=config.admin_group_id,
        document=message.document.file_id,
        caption=caption,
        parse_mode="HTML",
        reply_markup=get_submission_kb(user.id),
    )
    
    await message.answer(SUBMISSION_SENT)


@router.message(F.location)
async def handle_location(message: Message, bot: Bot) -> None:
    """Обработка геолокации.
    
    Requirements: 2.7, 2.10, 4.1-4.4
    """
    user = message.from_user
    if not user:
        return
    
    caption = format_submission_caption(
        user_id=user.id,
        full_name=user.full_name,
        username=user.username,
    )
    
    # location не поддерживает caption, отправляем текст отдельно
    caption_msg = await bot.send_message(
        chat_id=config.admin_group_id,
        text=caption,
        parse_mode="HTML",
    )
    
    await bot.send_location(
        chat_id=config.admin_group_id,
        latitude=message.location.latitude,
        longitude=message.location.longitude,
        reply_markup=get_submission_kb(
            user_id=user.id,
            first_msg_id=caption_msg.message_id,
            last_msg_id=caption_msg.message_id
        ),
    )
    
    await message.answer(SUBMISSION_SENT)


@router.message(F.contact)
async def handle_contact(message: Message, bot: Bot) -> None:
    """Обработка контактов.
    
    Requirements: 2.8, 2.10, 4.1-4.4
    """
    user = message.from_user
    if not user:
        return
    
    caption = format_submission_caption(
        user_id=user.id,
        full_name=user.full_name,
        username=user.username,
    )
    
    # contact не поддерживает caption, отправляем текст отдельно
    caption_msg = await bot.send_message(
        chat_id=config.admin_group_id,
        text=caption,
        parse_mode="HTML",
    )
    
    await bot.send_contact(
        chat_id=config.admin_group_id,
        phone_number=message.contact.phone_number,
        first_name=message.contact.first_name,
        last_name=message.contact.last_name,
        reply_markup=get_submission_kb(
            user_id=user.id,
            first_msg_id=caption_msg.message_id,
            last_msg_id=caption_msg.message_id
        ),
    )
    
    await message.answer(SUBMISSION_SENT)



@router.message(F.media_group_id)
async def handle_album(message: Message, bot: Bot, album: list[Message] | None = None) -> None:
    """Обработка альбомов (MediaGroup).
    
    AlbumMiddleware собирает все элементы альбома и передаёт их в album.
    Клавиатура прикрепляется только к последнему сообщению.
    
    Requirements: 2.9, 4.5
    """
    # Если album не передан, значит middleware ещё собирает
    if not album:
        return
    
    user = message.from_user
    if not user:
        return
    
    caption = format_submission_caption(
        user_id=user.id,
        full_name=user.full_name,
        username=user.username,
    )
    
    # Добавляем оригинальную подпись из первого сообщения если есть
    first_caption = album[0].caption
    if first_caption:
        safe_caption = escape_html(first_caption)
        caption = f"{caption}\n\n{safe_caption}"
    
    # Собираем InputMedia для отправки
    from aiogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument
    
    media_list = []
    for i, msg in enumerate(album):
        # Caption только на первом элементе
        item_caption = caption if i == 0 else None
        
        if msg.photo:
            media_list.append(InputMediaPhoto(
                media=msg.photo[-1].file_id,
                caption=item_caption,
                parse_mode="HTML" if item_caption else None,
            ))
        elif msg.video:
            media_list.append(InputMediaVideo(
                media=msg.video.file_id,
                caption=item_caption,
                parse_mode="HTML" if item_caption else None,
            ))
        elif msg.document:
            media_list.append(InputMediaDocument(
                media=msg.document.file_id,
                caption=item_caption,
                parse_mode="HTML" if item_caption else None,
            ))
    
    if not media_list:
        return
    
    # Отправляем альбом в админ-группу
    sent_messages = await bot.send_media_group(
        chat_id=config.admin_group_id,
        media=media_list,
    )
    
    # Клавиатура только на последнем сообщении альбома (Requirement 4.5)
    # send_media_group не поддерживает reply_markup, отправляем отдельно
    if sent_messages:
        first_msg = sent_messages[0]
        last_msg = sent_messages[-1]
        await bot.send_message(
            chat_id=config.admin_group_id,
            text="⬆️ Альбом выше",
            reply_to_message_id=last_msg.message_id,
            reply_markup=get_submission_kb(
                user_id=user.id,
                first_msg_id=first_msg.message_id,
                last_msg_id=last_msg.message_id
            ),
        )
    
    await message.answer(SUBMISSION_SENT)
