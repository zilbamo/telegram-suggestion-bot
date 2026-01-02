"""FSM states для рассылки сообщений."""

from aiogram.fsm.state import State, StatesGroup


class BroadcastStates(StatesGroup):
    """Состояния FSM для процесса рассылки.
    
    Поток:
    1. waiting_content - ожидание контента для рассылки от админа
    2. confirm - ожидание подтверждения отправки
    """
    
    waiting_content = State()
    confirm = State()
