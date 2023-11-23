from aiogram.fsm.state import State, StatesGroup


class StateTask(StatesGroup):
    STATE_CODE = State()
    STATE_INFO = State()
