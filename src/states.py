from aiogram.fsm.state import State, StatesGroup


class Service(StatesGroup):
    balance = State()
    bug = State()


class AdminService(StatesGroup):
    mailing_confirm = State()
    mailing_message = State()
