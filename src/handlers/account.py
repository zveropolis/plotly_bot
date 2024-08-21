import logging

import pandas as pd
from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.utils.formatting import as_list

import text
from core import exceptions as exc
from db import utils
from kb import get_account_keyboard

logger = logging.getLogger()
router = Router()


@router.message(Command("start"))
async def start_bot(message: Message):
    await message.answer(f"Добро пожаловать, {message.from_user.full_name}!")
    try:
        user_data = await utils.select_user(message.from_user.id)
    except exc.DB_error:
        await message.answer(text.DB_ERROR)
    else:
        await account_actions(message, user_data)


@router.message(Command("account"))
async def account_actions(message: Message, user_data: pd.DataFrame = None):
    if user_data is None:
        try:
            user_data = await utils.select_user(message.from_user.id)
        except exc.DB_error:
            await message.answer(text.DB_ERROR)
            return

    account_kb = get_account_keyboard(user_data)

    if user_data.empty:
        await message.answer(
            "Не вижу вас в базе данных. Хотите зарегистрироваться?",
            reply_markup=account_kb,
        )
    else:
        if len(user_data) != 1:
            logger.error(
                "Несколько пользователей имеют одинаковый id", extra=dict(user_data)
            )
        account_status = text.get_account_status(user_data)
        sub_status = text.get_sub_status(user_data)
        account_data = as_list(
            f"Статус аккаунта:  {account_status}",
            f"Статус подписки: {sub_status}" if sub_status else "",
        )

        await message.answer(**account_data.as_kwargs(), reply_markup=account_kb)
