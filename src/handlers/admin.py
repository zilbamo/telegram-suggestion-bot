"""Admin handlers для обработки callback-кнопок под заявками и рассылки."""

import asyncio

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from src.keyboards.callbacks import SubmissionAction, BroadcastAction
from src.keyboards.inline import get_broadcast_confirm_kb
from src.database import requests as db
from src.states.reply import ReplyStates
from src.states.broadcast import BroadcastStates
from src.config import config

router = Router(name="admin")


@router.callback_query(SubmissionAction.filter(F.action == "take"))
async def handle_take(callback: CallbackQuery, callback_data: SubmissionAction) -> None:
    """Обработка кнопки «Взял».
    
    - Удаляет inline-клавиатуру
    - Добавляет метку «✅ ОБРАБОТАНО (кем: @admin)»
    
    Requirements: 5.1, 5.2, 5.3
    """
    admin_username = callback.from_user.username or callback.from_user.full_name
    
    # Получаем текущий текст/caption сообщения
    message = callback.message
    
    processed_mark = f"\n\n✅ ОБРАБОТАНО (кем: @{admin_username})"
    
    try:
        if message.text:
            # Текстовое сообщение
            new_text = message.text + processed_mark
            await message.edit_text(text=new_text, reply_markup=None)
        elif message.caption:
            # Медиа с caption
            new_caption = message.caption + processed_mark
            await message.edit_caption(caption=new_caption, reply_markup=None)
        else:
            # Медиа без caption (voice, video_note, etc.)
            await message.edit_reply_markup(reply_markup=None)
            # Отправляем отдельное сообщение с меткой
            await message.reply(f"✅ ОБРАБОТАНО (кем: @{admin_username})")
    except TelegramBadRequest:
        # Сообщение уже изменено или удалено
        pass
    
    await callback.answer("Заявка взята в работу")


@router.callback_query(SubmissionAction.filter(F.action == "delete"))
async def handle_delete(callback: CallbackQuery, callback_data: SubmissionAction) -> None:
    """Обработка кнопки «Удалить».
    
    - Удаляет сообщение из админ-группы
    
    Requirements: 6.1
    """
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        # Сообщение уже удалено
        await callback.answer("Сообщение уже удалено")
        return
    
    await callback.answer("Заявка удалена")


@router.callback_query(SubmissionAction.filter(F.action == "ban"))
async def handle_ban(callback: CallbackQuery, callback_data: SubmissionAction) -> None:
    """Обработка кнопки «БАН».
    
    - Устанавливает is_banned=True в БД
    - Удаляет сообщение из админ-группы
    - Отправляет уведомление с автоудалением через 5 сек
    
    Requirements: 7.1, 7.2, 7.3, 7.4
    """
    user_id = callback_data.user_id
    
    # Баним пользователя в БД
    await db.ban_user(user_id)
    
    # Удаляем сообщение заявки
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    
    # Отправляем уведомление
    notification = await callback.message.answer(
        f"🚫 Пользователь ID {user_id} заблокирован"
    )
    
    # Автоудаление через 5 секунд
    await asyncio.sleep(5)
    try:
        await notification.delete()
    except TelegramBadRequest:
        pass
    
    await callback.answer("Пользователь заблокирован")


@router.callback_query(SubmissionAction.filter(F.action == "reply"))
async def handle_reply_start(
    callback: CallbackQuery, 
    callback_data: SubmissionAction,
    state: FSMContext
) -> None:
    """Обработка кнопки «Ответить» - запуск FSM.
    
    - Сохраняет target_user_id в state data
    - Переводит в состояние ожидания текста
    
    Requirements: 8.1
    """
    user_id = callback_data.user_id
    
    # Сохраняем ID пользователя для ответа
    await state.update_data(target_user_id=user_id)
    await state.set_state(ReplyStates.waiting_text)
    
    await callback.message.answer(
        f"✏️ Введите текст ответа для пользователя ID {user_id}:\n"
        f"(Отправьте /cancel для отмены)"
    )
    await callback.answer()


@router.message(ReplyStates.waiting_text, F.text == "/cancel")
async def handle_reply_cancel(message: Message, state: FSMContext) -> None:
    """Отмена ответа пользователю."""
    await state.clear()
    await message.answer("❌ Ответ отменён")


@router.message(ReplyStates.waiting_text, F.text)
async def handle_reply_text(message: Message, state: FSMContext, bot: Bot) -> None:
    """Получение текста ответа и отправка пользователю.
    
    - Отправляет текст пользователю от имени бота
    - Обрабатывает BotBlocked
    
    Requirements: 8.2, 8.3
    """
    data = await state.get_data()
    target_user_id = data.get("target_user_id")
    
    if not target_user_id:
        await message.answer("❌ Ошибка: не найден ID пользователя")
        await state.clear()
        return
    
    try:
        await bot.send_message(
            chat_id=target_user_id,
            text=f"📩 Ответ от администрации:\n\n{message.text}"
        )
        await message.answer("✅ Ответ отправлен пользователю")
    except TelegramForbiddenError:
        # Пользователь заблокировал бота
        await message.answer("❌ Доставка не удалась: пользователь заблокировал бота")
    except TelegramBadRequest as e:
        await message.answer(f"❌ Ошибка отправки: {e}")
    
    await state.clear()


# ==================== BROADCAST HANDLERS ====================


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext) -> None:
    """Команда /broadcast - запуск рассылки.
    
    - Проверяет, что отправитель в списке admin_ids
    - Запускает FSM BroadcastStates
    
    Requirements: 9.1, 9.2, 9.3
    """
    # Проверка админа по config.admin_ids
    if message.from_user.id not in config.admin_ids:
        # Игнорируем команду от не-админа (Requirements 9.2)
        return
    
    await state.set_state(BroadcastStates.waiting_content)
    await message.answer(
        "📢 <b>Рассылка</b>\n\n"
        "Отправьте контент для рассылки (текст, фото, видео и т.д.).\n"
        "Отправьте /cancel для отмены.",
        parse_mode="HTML"
    )


@router.message(BroadcastStates.waiting_content, F.text == "/cancel")
async def broadcast_cancel_content(message: Message, state: FSMContext) -> None:
    """Отмена рассылки на этапе ввода контента."""
    await state.clear()
    await message.answer("❌ Рассылка отменена")


@router.message(BroadcastStates.waiting_content)
async def broadcast_receive_content(message: Message, state: FSMContext) -> None:
    """Получение контента для рассылки и показ превью.
    
    - Сохраняет message_id и chat_id для copy_message
    - Показывает превью с кнопками подтверждения
    
    Requirements: 9.3, 9.4
    """
    # Сохраняем данные сообщения для copy_message
    await state.update_data(
        broadcast_chat_id=message.chat.id,
        broadcast_message_id=message.message_id
    )
    await state.set_state(BroadcastStates.confirm)
    
    await message.answer(
        "👆 <b>Превью сообщения выше</b>\n\n"
        "Подтвердите отправку рассылки всем пользователям:",
        parse_mode="HTML",
        reply_markup=get_broadcast_confirm_kb()
    )


@router.callback_query(BroadcastStates.confirm, BroadcastAction.filter(F.action == "cancel"))
async def broadcast_cancel_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    """Отмена рассылки на этапе подтверждения.
    
    Requirements: 9.6
    """
    await state.clear()
    await callback.message.edit_text("❌ Рассылка отменена")
    await callback.answer()


@router.callback_query(BroadcastStates.confirm, BroadcastAction.filter(F.action == "send"))
async def broadcast_send(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """Запуск асинхронной рассылки.
    
    - copy_message для всех активных пользователей
    - Rate limiting 25 msg/sec (asyncio.sleep(0.04))
    - Обработка BotBlocked → is_active=False
    - Статистика по завершении
    
    Requirements: 9.5, 9.7, 9.8, 9.9
    """
    data = await state.get_data()
    broadcast_chat_id = data.get("broadcast_chat_id")
    broadcast_message_id = data.get("broadcast_message_id")
    
    if not broadcast_chat_id or not broadcast_message_id:
        await callback.message.edit_text("❌ Ошибка: контент рассылки не найден")
        await state.clear()
        await callback.answer()
        return
    
    # Убираем кнопки и показываем статус
    await callback.message.edit_text("⏳ Рассылка запущена...")
    await callback.answer()
    
    # Получаем всех активных пользователей (is_banned=False)
    users = await db.get_active_users()
    
    sent_count = 0
    failed_count = 0
    
    for user in users:
        try:
            await bot.copy_message(
                chat_id=user.user_id,
                from_chat_id=broadcast_chat_id,
                message_id=broadcast_message_id
            )
            sent_count += 1
        except TelegramForbiddenError:
            # Пользователь заблокировал бота → is_active=False
            await db.set_user_inactive(user.user_id)
            failed_count += 1
        except TelegramBadRequest:
            # Другие ошибки (чат не найден и т.д.)
            failed_count += 1
        
        # Rate limiting: 20 msg/sec = 0.05 sec между сообщениями (безопаснее лимитов Telegram)
        await asyncio.sleep(0.05)
    
    # Статистика по завершении
    await callback.message.edit_text(
        f"✅ <b>Рассылка завершена</b>\n\n"
        f"📤 Отправлено: {sent_count}\n"
        f"❌ Неактивных/Заблок: {failed_count}",
        parse_mode="HTML"
    )
    
    await state.clear()
