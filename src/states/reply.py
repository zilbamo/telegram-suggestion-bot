"""FSM states для ответа пользователю."""

from aiogram.fsm.state import State, StatesGroup


class ReplyStates(StatesGroup):
    """Состояния FSM для ответа пользователю от админа.
    
    Поток:
    1. Админ нажимает кнопку «Ответить» → сохраняем target_user_id в state data
    2. waiting_text - ожидание текста ответа от админа
    3. Отправляем текст пользователю → очищаем state
    
    State data:
        target_user_id (int): ID пользователя, которому отправляем ответ
    """
    
    waiting_text = State()
