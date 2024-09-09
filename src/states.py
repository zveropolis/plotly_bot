from aiogram.fsm.state import State, StatesGroup


class Service(StatesGroup):
    sub = State()


class AdminService(StatesGroup):
    mailing_confirm = State()
    mailing_message = State()
