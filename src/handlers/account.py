import logging

from aiogram import F, Router
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.formatting import as_list

import text
from core import exceptions as exc
from core.metric import async_speed_metric
from db import utils
from db.models import UserData
from kb import get_account_keyboard, static_start_button

logger = logging.getLogger()
router = Router()


@router.message(Command("start"))
@router.message(F.text == "🔄")
@async_speed_metric
async def start_bot(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state()

    await message.answer(
        f"Добро пожаловать, {message.from_user.full_name}!",
        reply_markup=static_start_button,
    )
    try:
        await utils.clear_cash(message.from_user.id)
        user_data = await utils.get_user(message.from_user.id)
    except exc.DatabaseError:
        await message.answer(text.DB_ERROR)
    else:
        await account_actions(message, user_data)


@router.message(Command("account"))
@router.message(Command("app"))
@router.message(F.text == "Статус")
@async_speed_metric
async def account_actions(
    message: Message, user_data: UserData = None, usr_id: int = None
):
    if user_data is None:
        try:
            user_data = await utils.get_user(usr_id if usr_id else message.from_user.id)
        except exc.DatabaseError:
            await message.answer(text.DB_ERROR)
            return

    account_kb = get_account_keyboard(user_data)

    if user_data is None:
        await message.answer(
            "Не вижу вас в базе данных. Хотите зарегистрироваться?",
            reply_markup=account_kb,
        )
    else:
        account_status = text.get_account_status(user_data)
        sub_status = text.get_sub_status(user_data)
        account_data = as_list(
            f"Статус аккаунта:  {account_status}",
            f"Статус подписки: {sub_status}" if sub_status else "",
        )

        await message.answer(**account_data.as_kwargs(), reply_markup=account_kb)
