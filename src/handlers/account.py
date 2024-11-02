import logging
from typing import Union

from aiogram import F, Router
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.formatting import as_list

import text
from core import exceptions as exc
from core.metric import async_speed_metric
from db import utils
from db.models import UserData
from kb import get_account_keyboard, static_start_button
from messages import INTRO

logger = logging.getLogger()
router = Router()


@router.message(Command("start"))
@router.message(F.text == "Перезагрузка")
@router.callback_query(F.data == "start_app")
@async_speed_metric
async def start_bot(trigger: Union[Message, CallbackQuery], state: FSMContext):
    await state.clear()
    await state.set_state()

    await getattr(trigger, "message", trigger).answer(
        f"Добро пожаловать, {trigger.from_user.full_name}!"
        "\nЯ бот для управления VPN сервисом DanVPN.",
        reply_markup=static_start_button,
    )

    if INTRO:
        await getattr(trigger, "message", trigger).answer(INTRO)

    try:
        await utils.clear_cash(trigger.from_user.id)
        user_data = await utils.get_user(trigger.from_user.id)
    except exc.DatabaseError:
        await getattr(trigger, "message", trigger).answer(text.DB_ERROR)
    else:
        await account_actions(trigger, user_data)


@router.message(Command("account"))
@router.message(Command("app"))
@router.message(F.text == "Статус")
@async_speed_metric
async def account_actions(
    trigger: Union[Message, CallbackQuery],
    user_data: UserData = None,
    usr_id: int = None,
):
    if user_data is None:
        try:
            user_data = await utils.get_user(usr_id if usr_id else trigger.from_user.id)
        except exc.DatabaseError:
            await getattr(trigger, "message", trigger).answer(text.DB_ERROR)
            return

    account_kb = get_account_keyboard(user_data)

    if user_data is None:
        await getattr(trigger, "message", trigger).answer(
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

        await getattr(trigger, "message", trigger).answer(
            **account_data.as_kwargs(), reply_markup=account_kb
        )
