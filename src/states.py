from aiogram.fsm.state import State, StatesGroup


class Service(StatesGroup):
    sub = State()
