"""FSM states для админ-панели."""

from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    """Состояния FSM для админ-панели."""
    
    waiting_unban_id = State()  # Ожидание ID для разбана
